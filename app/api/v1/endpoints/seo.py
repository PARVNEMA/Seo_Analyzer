import os
import json
import uuid
import tempfile
import subprocess
from fastapi import APIRouter, HTTPException
from app.schemas.seo import SEOAnalyzeRequest, SEOReportResponse
from app.services.seo_ai import generate_seo_suggestions
from app.services.technical_audit import analyze_readability, fetch_pagespeed_data
from app.db.supabase import save_seo_report

router = APIRouter()

@router.get("/test-crawl")
async def test_crawl(url: str):
    """
    Test endpoint to check if Scrapy is able to crawl a website successfully.
    Returns the raw parsed Scrapy data without running AI suggestions or DB saves.
    """
    task_id = str(uuid.uuid4())
    temp_dir = tempfile.gettempdir()
    output_file = os.path.join(temp_dir, f"scrapy_{task_id}.json")
    
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        scraper_dir = os.path.join(project_root, "scraper")
        
        # Run spider as a subprocess using uv run for correct environment context
        result = subprocess.run(
            ["uv", "run", "scrapy", "crawl", "seo", "-a", f"url={url}", "-o", output_file],
            cwd=scraper_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Scrapy failed (exit code {result.returncode}): {result.stderr or result.stdout}")
            
        if not os.path.exists(output_file):
            raise Exception(f"Output file was not created. Subprocess output: {result.stdout}\nStderr: {result.stderr}")
            
        with open(output_file, 'r', encoding='utf-8') as f:
            scrapy_data = json.load(f)
            if isinstance(scrapy_data, list) and len(scrapy_data) > 0:
                scrapy_data = scrapy_data[0]
            else:
                scrapy_data = {}
                
        return {
            "status": "success",
            "crawled_data": scrapy_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to crawl URL: {str(e)}")
    finally:
        # Cleanup temp file
        if os.path.exists(output_file):
            os.remove(output_file)


@router.post("/analyze", response_model=SEOReportResponse)
async def analyze_seo(request: SEOAnalyzeRequest):
    """
    Analyze a given URL for SEO metrics and generate AI suggestions.
    """
    url_str = str(request.url)
    keyword = request.keyword
    
    # We will use a unique task ID to save the Scrapy output
    task_id = str(uuid.uuid4())
    temp_dir = tempfile.gettempdir()
    output_file = os.path.join(temp_dir, f"scrapy_{task_id}.json")
    
    # 1. Trigger Scrapy Spider
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        scraper_dir = os.path.join(project_root, "scraper")
        
        # Run spider as a subprocess using uv run for correct environment context
        result = subprocess.run(
            ["uv", "run", "scrapy", "crawl", "seo", "-a", f"url={url_str}", "-o", output_file],
            cwd=scraper_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Scrapy failed: {result.stderr}")
            
        if not os.path.exists(output_file):
            raise Exception("Output file was not created by crawler.")
            
        with open(output_file, 'r', encoding='utf-8') as f:
            scrapy_data = json.load(f)
            if isinstance(scrapy_data, list) and len(scrapy_data) > 0:
                scrapy_data = scrapy_data[0]
            else:
                scrapy_data = {}
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to crawl URL: {str(e)}")
    finally:
        # Cleanup temp file
        if os.path.exists(output_file):
            os.remove(output_file)

    # Extract parsed data
    title = scrapy_data.get("title")
    meta = scrapy_data.get("meta_description")
    text_content = scrapy_data.get("text_content", "")
    
    # 2. Technical & Readability Analysis
    readability = analyze_readability(text_content)
    pagespeed = fetch_pagespeed_data(url_str)
    
    # Word count and Keyword density
    words = text_content.split()
    word_count = len(words)
    keyword_density = 0.0
    if keyword and word_count > 0:
        keyword_lower = keyword.lower()
        count = text_content.lower().count(keyword_lower)
        keyword_density = (count / word_count) * 100
        
    # 3. AI Suggestions (Langchain)
    ai_recommendations = generate_seo_suggestions(
        title=title,
        meta=meta,
        content=text_content,
        keyword=keyword
    )
    
    # 4. Construct Response
    report = SEOReportResponse(
        url=url_str,
        keyword=keyword,
        title=title,
        meta_description=meta,
        word_count=word_count,
        keyword_density=keyword_density if keyword else None,
        readability_score=readability["score"],
        readability_feedback=readability["feedback"],
        missing_alt_images=scrapy_data.get("missing_alt_images", 0),
        total_images=scrapy_data.get("total_images", 0),
        broken_links=scrapy_data.get("broken_links", 0),
        total_links=scrapy_data.get("total_links", 0),
        title_suggestions=ai_recommendations.title_suggestions,
        meta_suggestions=ai_recommendations.meta_suggestions,
        pagespeed_score=pagespeed
    )
    
    # 5. Save to Supabase
    save_seo_report(report.model_dump())
    
    return report
