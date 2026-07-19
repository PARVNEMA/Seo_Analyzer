import uuid
import asyncio
from fastapi import APIRouter, Depends, BackgroundTasks
from typing import Dict, Any

from app.db.supabase import get_supabase_client
from app.services.crawler_service import start_crawl_process
from app.dependencies.auth import get_current_user

router = APIRouter()

@router.post("/crawl")
async def start_crawl(target_url: str, background_tasks: BackgroundTasks, user = Depends(get_current_user)) -> Dict[str, Any]:
    supabase = get_supabase_client()

    # Check for existing job by this user for the same URL and job_type
    try:
        existing_job = supabase.table("crawl_jobs").select("*").eq("target_url", target_url).eq("created_by", user.id).eq("job_type", "crawl").execute()
        if existing_job.data:
            job = existing_job.data[0]
            return {"job_id": job["id"], "status": job["status"], "message": "Returning existing crawl job"}
    except Exception as e:
        print(f"Error checking existing job: {e}")

    job_id = str(uuid.uuid4())

    # Store crawl job in Supabase
    try:
        supabase.table("crawl_jobs").insert({
            "id": job_id,
            "target_url": target_url,
            "job_type": "crawl",
            "status": "pending",
            "created_by": user.id
        }).execute()
    except Exception as e:
        print(f"Error inserting job to Supabase: {e}")
        # Proceeding anyway just in case the table isn't created yet or we are testing locally

    background_tasks.add_task(start_crawl_process, job_id, target_url, "site_spider")

    return {"job_id": job_id, "status": "pending", "message": "Crawl job started"}

@router.post("/crawl-seo")
async def start_crawl_seo(target_url: str, background_tasks: BackgroundTasks, user = Depends(get_current_user)) -> Dict[str, Any]:
    supabase = get_supabase_client()

    # Check for existing job by this user for the same URL and job_type
    try:
        existing_job = supabase.table("crawl_jobs").select("*").eq("target_url", target_url).eq("created_by", user.id).eq("job_type", "crawl-seo").eq("status","limit_reached").execute()
        if existing_job.data:
            job = existing_job.data[0]
            return {"job_id": job["id"], "status": job["status"], "message": "Returning existing SEO crawl job"}
    except Exception as e:
        print(f"Error checking existing job: {e}")

    job_id = str(uuid.uuid4())

    # Store crawl job in Supabase
    try:
        supabase.table("crawl_jobs").insert({
            "id": job_id,
            "target_url": target_url,
            "job_type": "crawl-seo",
            "status": "pending",
            "created_by": user.id
        }).execute()
    except Exception as e:
        print(f"Error inserting job to Supabase: {e}")

    background_tasks.add_task(start_crawl_process, job_id, target_url, "site_seo_spider")

    return {"job_id": job_id, "status": "pending", "message": "SEO crawl job started"}

@router.get("/jobs")
async def list_crawl_jobs(user = Depends(get_current_user)):
    """
    List all previously crawled websites (jobs).
    """
    supabase = get_supabase_client()
    try:
        # Fetch all crawl jobs ordered by latest first, filtered by current user
        response = supabase.table("crawl_jobs").select("*").eq("created_by", user.id).order("created_at", desc=True).execute()
        return {"status": "success", "jobs": response.data}
    except Exception as e:
        return {"status": "error", "message": str(e)}
