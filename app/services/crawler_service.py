import asyncio
import logging
import os
import sys
import subprocess
from typing import Dict

logger = logging.getLogger(__name__)

# Store active processes by job_id
active_crawlers: Dict[str, subprocess.Popen] = {}
cancelled_jobs = set()

def stop_crawl_process(job_id: str) -> bool:
    """Stops an active crawler process by job_id."""
    process = active_crawlers.get(job_id)
    if process:
        try:
            logger.info(f"Stopping crawler process for job {job_id}")
            cancelled_jobs.add(job_id)
            process.terminate()
            return True
        except Exception as e:
            logger.error(f"Failed to stop process for job {job_id}: {e}")
            return False
    return False

def run_scrapy_process(job_id: str, target_url: str, spider_name: str, scraper_dir: str):
    """
    Runs the Scrapy process using the python subprocess module.
    """
    from app.core.config import get_settings
    settings = get_settings()

    cmd = [
        sys.executable, "-m", "scrapy", "crawl", spider_name,
        "-a", f"start_url={target_url}",
        "-a", f"job_id={job_id}",
        "-s", f"CLOSESPIDER_PAGECOUNT={settings.MAX_CRAWL_PAGES}"
    ]
    
    logger.info(f"Starting Scrapy process for job {job_id}: {' '.join(cmd)}")
    
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(sys.path)
    
    process = subprocess.Popen(
        cmd,
        cwd=scraper_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    active_crawlers[job_id] = process
    
    stdout, stderr = process.communicate()
    
    if job_id in active_crawlers:
        del active_crawlers[job_id]
        
    is_cancelled = job_id in cancelled_jobs
    if is_cancelled:
        cancelled_jobs.discard(job_id)
        
    stderr_str = stderr.decode('utf-8', errors='ignore')
    
    if is_cancelled:
        logger.info(f"Scrapy job {job_id} was manually cancelled.")
        final_status = "cancelled"
    elif process.returncode == 0:
        logger.info(f"Scrapy job {job_id} completed successfully.")
        final_status = "limit_reached" if "closespider_pagecount" in stderr_str else "completed"
    else:
        logger.error(f"Scrapy job {job_id} failed with code {process.returncode}")
        logger.error(f"Stderr: {stderr_str}")
        final_status = "failed"
        
    # Update job status in Supabase and generate embeddings for whatever was crawled
    from app.db.supabase import get_supabase_client
    from app.services.embedding_service import process_and_store_embeddings
    
    try:
        supabase = get_supabase_client()
        supabase.table("crawl_jobs").update({"status": final_status}).eq("id", job_id).execute()
        
        # Notify WebSocket that the crawl has finished
        import requests
        import os
        port = os.environ.get("PORT", "8000")
        webhook_url = f"http://127.0.0.1:{port}/api/v1/webhook/crawls/{job_id}"
        try:
            requests.post(webhook_url, json={"status": final_status, "job_id": job_id}, timeout=3)
        except Exception as e:
            logger.error(f"Failed to notify webhook of completion: {e}")
            
    except Exception as e:
        logger.error(f"Failed to update job status or generate embeddings: {e}")

async def start_crawl_process(job_id: str, target_url: str, spider_name: str):
    """
    Spawns a new Scrapy process inside a separate thread.
    This prevents blocking the FastAPI event loop.
    """
    try:
        # Determine the path to the scrapy project
        scraper_dir = os.path.join(os.getcwd(), "scraper")
        
        # Run the synchronous subprocess code in a separate thread
        await asyncio.to_thread(run_scrapy_process, job_id, target_url, spider_name, scraper_dir)
                
    except Exception as e:
        logger.error(f"Failed to start Scrapy process: {e}")
