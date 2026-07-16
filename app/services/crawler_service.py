import asyncio
import logging
import os
import sys
import subprocess
from typing import Dict

logger = logging.getLogger(__name__)

# Store active processes by job_id
active_crawlers: Dict[str, subprocess.Popen] = {}

def stop_crawl_process(job_id: str) -> bool:
    """Stops an active crawler process by job_id."""
    process = active_crawlers.get(job_id)
    if process:
        try:
            logger.info(f"Stopping crawler process for job {job_id}")
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
    
    process = subprocess.Popen(
        cmd,
        cwd=scraper_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    active_crawlers[job_id] = process
    
    stdout, stderr = process.communicate()
    
    if job_id in active_crawlers:
        del active_crawlers[job_id]
    
    if process.returncode == 0:
        logger.info(f"Scrapy job {job_id} completed successfully.")
        
        # Check if it was closed due to limit
        stderr_str = stderr.decode('utf-8', errors='ignore')
        final_status = "limit_reached" if "closespider_pagecount" in stderr_str else "completed"
        
        # Update job status in Supabase
        from app.db.supabase import get_supabase_client
        from app.services.embedding_service import process_and_store_embeddings
        try:
            supabase = get_supabase_client()
            supabase.table("crawl_jobs").update({"status": final_status}).eq("id", job_id).execute()
            
            # Fetch all crawl_results for this job to generate embeddings
            results = supabase.table("crawl_results").select("id, text_content, title, meta_description").eq("job_id", job_id).execute()
            if results.data:
                logger.info(f"Generating embeddings for {len(results.data)} pages from job {job_id}")
                for row in results.data:
                    if row.get("text_content"):
                        process_and_store_embeddings(
                            crawl_result_id=row["id"], 
                            text_content=row["text_content"],
                            title=row.get("title"),
                            meta_description=row.get("meta_description"),
                            metadata={"job_id": job_id}
                        )
        except Exception as e:
            logger.error(f"Failed to update job status or generate embeddings: {e}")
    else:
        logger.error(f"Scrapy job {job_id} failed with code {process.returncode}")
        logger.error(f"Stderr: {stderr.decode()}")
        from app.db.supabase import get_supabase_client
        try:
            supabase = get_supabase_client()
            supabase.table("crawl_jobs").update({"status": "failed"}).eq("id", job_id).execute()
        except Exception as e:
            logger.error(f"Failed to update job status in Supabase: {e}")

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
