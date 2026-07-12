import os
import json
import uuid
import tempfile
import subprocess
from app.graph.state import AgentState
from app.services.technical_audit import analyze_readability, fetch_pagespeed_data
from app.services.seo_ai import generate_seo_suggestions
from app.core.llm_factory import get_llm
from pydantic import BaseModel, Field
from app.services.competitor_scraper import fetch_competitor_data, RateLimitException

def crawler_node(state: AgentState) -> dict:
    url = state.get("url")
    if not url:
        return {"errors": ["No URL provided for crawling"]}

    task_id = str(uuid.uuid4())
    temp_dir = tempfile.gettempdir()
    output_file = os.path.join(temp_dir, f"scrapy_{task_id}.json")

    try:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        scraper_dir = os.path.join(project_root, "scraper")

        result = subprocess.run(
            ["uv", "run", "scrapy", "crawl", "seo", "-a", f"url={url}", "-o", output_file],
            cwd=scraper_dir,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return {"errors": [f"Scrapy failed: {result.stderr}"]}

        if not os.path.exists(output_file):
            return {"errors": ["Output file was not created by crawler."]}

        with open(output_file, 'r', encoding='utf-8') as f:
            scrapy_data = json.load(f)
            if isinstance(scrapy_data, list) and len(scrapy_data) > 0:
                scrapy_data = scrapy_data[0]
            else:
                scrapy_data = {}

        raw_content = scrapy_data.get("text_content", "")
        tech_metrics = state.get("technical_metrics", {})
        tech_metrics["missing_alt_images"] = scrapy_data.get("missing_alt_images", 0)
        tech_metrics["total_images"] = scrapy_data.get("total_images", 0)
        tech_metrics["broken_links"] = scrapy_data.get("broken_links", 0)
        tech_metrics["total_links"] = scrapy_data.get("total_links", 0)

        on_page = state.get("on_page_metrics", {})
        on_page["title"] = scrapy_data.get("title")
        on_page["meta_description"] = scrapy_data.get("meta_description")

        return {
            "raw_content": raw_content,
            "technical_metrics": tech_metrics,
            "on_page_metrics": on_page
        }
    except Exception as e:
        return {"errors": [f"Crawler node failed: {str(e)}"]}
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)

def technical_audit_node(state: AgentState) -> dict:
    url = state.get("url")
    raw_content = state.get("raw_content", "")
    tech_metrics = state.get("technical_metrics", {})

    readability = analyze_readability(raw_content)
    pagespeed = fetch_pagespeed_data(url) if url else None

    tech_metrics["readability_score"] = readability.get("score")
    tech_metrics["readability_feedback"] = readability.get("feedback")
    tech_metrics["pagespeed_score"] = pagespeed

    return {"technical_metrics": tech_metrics}

def on_page_audit_node(state: AgentState) -> dict:
    raw_content = state.get("raw_content", "")
    keyword = state.get("target_keyword")
    on_page = state.get("on_page_metrics", {})

    words = raw_content.split()
    word_count = len(words)
    keyword_density = 0.0

    if keyword and word_count > 0:
        keyword_lower = keyword.lower()
        count = raw_content.lower().count(keyword_lower)
        keyword_density = (count / word_count) * 100

    on_page["word_count"] = word_count
    on_page["keyword_density"] = keyword_density

    # Generate suggestions
    title = on_page.get("title")
    meta = on_page.get("meta_description")

    ai_recs = generate_seo_suggestions(title, meta, raw_content, keyword)
    on_page["title_suggestions"] = [s.model_dump() for s in ai_recs.title_suggestions]
    on_page["meta_suggestions"] = [s.model_dump() for s in ai_recs.meta_suggestions]

    return {"on_page_metrics": on_page}

class IntentClassification(BaseModel):
    intent: str = Field(description="The primary search intent: Informational, Navigational, Commercial, or Transactional.")
    reasoning: str = Field(description="Reasoning for this classification.")

def intent_classifier_node(state: AgentState) -> dict:
    keyword = state.get("target_keyword")
    if not keyword:
        return {}

    llm = get_llm().with_structured_output(IntentClassification)
    prompt = f"Analyze the search intent for the keyword '{keyword}'. Classify it into Informational, Navigational, Commercial, or Transactional."
    try:
        classification = llm.invoke(prompt)
        content_gap = state.get("content_gap_analysis", {})
        content_gap["intent"] = classification.intent
        content_gap["intent_reasoning"] = classification.reasoning
        return {"content_gap_analysis": content_gap}
    except Exception as e:
        errors = state.get("errors", [])
        errors.append(f"Intent classification failed: {str(e)}")
        return {"errors": errors}

def competitor_scraper_node(state: AgentState) -> dict:
    keyword = state.get("target_keyword")
    if not keyword:
        return {}

    try:
        competitor_data = fetch_competitor_data(keyword)
        if "error" in competitor_data:
            errors = state.get("errors", [])
            errors.append(f"Competitor Scraper Error: {competitor_data['error']}")
            return {"errors": errors}

        return {"competitor_data": competitor_data}
    except RateLimitException as e:
        errors = state.get("errors", [])
        errors.append("SERP API rate limit hit. Skipping competitor analysis.")
        return {"errors": errors}
    except Exception as e:
        errors = state.get("errors", [])
        errors.append(f"Competitor scraper node failed: {str(e)}")
        return {"errors": errors}

def report_generator_node(state: AgentState) -> dict:
    # Synthesize everything into final report
    report = {
        "url": state.get("url"),
        "target_keyword": state.get("target_keyword"),
        "technical": state.get("technical_metrics"),
        "on_page": state.get("on_page_metrics"),
        "content_gap": state.get("content_gap_analysis"),
        "errors": state.get("errors")
    }
    return {"final_report": report}
