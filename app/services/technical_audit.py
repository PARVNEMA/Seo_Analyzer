import textstat
from typing import Dict, Any, Optional

def analyze_readability(text: str) -> Dict[str, Any]:
    if not text or not text.strip():
        return {
            "score": 0.0,
            "feedback": "No content found to analyze readability."
        }
        
    score = textstat.flesch_reading_ease(text)
    
    # Provide plain-language feedback
    if score >= 90:
        feedback = "Very easy to read. Easily understood by an average 11-year-old student."
    elif score >= 80:
        feedback = "Easy to read. Conversational English for consumers."
    elif score >= 70:
        feedback = "Fairly easy to read."
    elif score >= 60:
        feedback = "Plain English. Easily understood by 13- to 15-year-old students."
    elif score >= 50:
        feedback = "Fairly difficult to read."
    elif score >= 30:
        feedback = "Difficult to read. Best understood by college graduates."
    else:
        feedback = "Very difficult to read. Best understood by university graduates."
        
    return {
        "score": score,
        "feedback": feedback
    }

def fetch_pagespeed_data(url: str) -> Optional[int]:
    """
    Placeholder for Google PageSpeed Insights API call.
    In Phase 1, we return None or a mocked score if an API key isn't provided yet.
    """
    # For now, returning None as we agreed to gracefully handle missing PageSpeed API key
    return None
