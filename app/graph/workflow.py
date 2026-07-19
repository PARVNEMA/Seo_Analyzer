import os
import sqlite3
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.memory import InMemorySaver

from app.graph.state import AgentState
from app.graph.nodes import (
    crawler_node,
    technical_audit_node,
    on_page_audit_node,
    intent_classifier_node,
    competitor_scraper_node,
    report_generator_node,
)

# Initialize the StateGraph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("crawler", crawler_node)
workflow.add_node("technical_audit", technical_audit_node)
workflow.add_node("on_page_audit", on_page_audit_node)
workflow.add_node("intent_classifier", intent_classifier_node)
workflow.add_node("competitor_scraper", competitor_scraper_node)
workflow.add_node("report_generator", report_generator_node)

# Set Entry Point
workflow.set_entry_point("crawler")

# Define Routing Functions
def route_after_crawler(state: AgentState):
    if state.get("errors"):
        return "report_generator"
    return "technical_audit"

def route_after_on_page(state: AgentState):
    if not state.get("target_keyword"):
        return "report_generator"
    return "intent_classifier"

def route_after_competitor(state: AgentState):
    # Even if there's an error in competitor scraper (e.g. rate limit),
    # we just proceed to report generation and surface the error gracefully.
    return "report_generator"

# Add Edges
workflow.add_conditional_edges(
    "crawler",
    route_after_crawler,
    {
        "technical_audit": "technical_audit",
        "report_generator": "report_generator"
    }
)

workflow.add_edge("technical_audit", "on_page_audit")

workflow.add_conditional_edges(
    "on_page_audit",
    route_after_on_page,
    {
        "intent_classifier": "intent_classifier",
        "report_generator": "report_generator"
    }
)

workflow.add_edge("intent_classifier", "competitor_scraper")

workflow.add_conditional_edges(
    "competitor_scraper",
    route_after_competitor,
    {
        "report_generator": "report_generator"
    }
)

workflow.add_edge("report_generator", END)

# Set up local sqlite DB for Checkpointer
# PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
# DB_PATH = os.path.join(PROJECT_ROOT, "langgraph_state.sqlite")

# conn = sqlite3.connect(DB_PATH, check_same_thread=False)
# checkpointer = SqliteSaver(conn)
checkpointer = InMemorySaver()


# print('workflow',workflow)

# Compile the Graph
seo_graph = workflow.compile(checkpointer=checkpointer)
