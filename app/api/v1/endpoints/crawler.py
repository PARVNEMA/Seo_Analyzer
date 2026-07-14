import uuid
import asyncio
from fastapi import APIRouter, Depends, BackgroundTasks
from typing import Dict, Any

from app.db.supabase import get_supabase_client
from app.services.crawler_service import start_crawl_process

router = APIRouter()

@router.post("/crawl")
async def start_crawl(target_url: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    job_id = str(uuid.uuid4())
    supabase = get_supabase_client()
    
    # Store crawl job in Supabase
    try:
        supabase.table("crawl_jobs").insert({
            "id": job_id,
            "target_url": target_url,
            "job_type": "crawl",
            "status": "pending"
        }).execute()
    except Exception as e:
        print(f"Error inserting job to Supabase: {e}")
        # Proceeding anyway just in case the table isn't created yet or we are testing locally
    
    background_tasks.add_task(start_crawl_process, job_id, target_url, "site_spider")
    
    return {"job_id": job_id, "status": "pending", "message": "Crawl job started"}

@router.post("/crawl-seo")
async def start_crawl_seo(target_url: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    job_id = str(uuid.uuid4())
    supabase = get_supabase_client()
    
    # Store crawl job in Supabase
    try:
        supabase.table("crawl_jobs").insert({
            "id": job_id,
            "target_url": target_url,
            "job_type": "crawl-seo",
            "status": "pending"
        }).execute()
    except Exception as e:
        print(f"Error inserting job to Supabase: {e}")
    
    background_tasks.add_task(start_crawl_process, job_id, target_url, "site_seo_spider")
    
    return {"job_id": job_id, "status": "pending", "message": "SEO crawl job started"}
