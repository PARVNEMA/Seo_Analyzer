from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, BackgroundTasks
from typing import Dict, List, Any
import json
from app.services.crawler_service import stop_crawl_process
from app.dependencies.auth import get_current_user_ws, get_current_user


router = APIRouter()

# Store active websocket connections per job_id
# job_id -> list of active connections
active_connections: Dict[str, List[WebSocket]] = {}

@router.websocket("/ws/crawls/{job_id}")
async def crawl_websocket(websocket: WebSocket, job_id: str, user= Depends(get_current_user_ws)):
    await websocket.accept()
    if job_id not in active_connections:
        active_connections[job_id] = []
    active_connections[job_id].append(websocket)

    try:
        while True:
            # Keep connection open, client might send messages
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("action") == "stop":
                    stop_crawl_process(job_id)
                    await websocket.send_json({"status": "stopped", "message": "Crawler stopped by user"})
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        active_connections[job_id].remove(websocket)
        if not active_connections[job_id]:
            del active_connections[job_id]

@router.post("/webhook/crawls/{job_id}")
async def crawl_webhook(job_id: str, data: Dict[str, Any], background_tasks: BackgroundTasks):
    """
    Webhook endpoint for the Scrapy pipeline to post real-time updates.
    These updates are saved to Supabase and broadcasted to WebSockets.
    """
    from app.db.supabase import get_supabase_client
    from app.services.embedding_service import process_and_store_embeddings

    # Extract text_content so it's not saved to the main table, saving huge amounts of space
    text_content = data.pop("text_content", None)
    title = data.get("title")
    meta_description = data.get("meta_description")

    # Save to Supabase
    if "status" not in data or len(data) > 2:
        try:
            supabase = get_supabase_client()
            result = supabase.table("crawl_results").insert(data).execute()
            
            # If we got an ID and have text content, schedule embedding generation in the background
            if text_content and result.data and len(result.data) > 0:
                crawl_result_id = result.data[0]["id"]
                background_tasks.add_task(
                    process_and_store_embeddings,
                    crawl_result_id=crawl_result_id,
                    text_content=text_content,
                    title=title,
                    meta_description=meta_description,
                    metadata={"job_id": job_id}
                )
        except Exception as e:
            print(f"Failed to save result to Supabase: {e}")

    # Broadcast to WebSockets
    if job_id in active_connections:
        dead_connections = []
        for connection in active_connections[job_id]:
            try:
                await connection.send_json(data)
            except Exception:
                dead_connections.append(connection)

        for connection in dead_connections:
            active_connections[job_id].remove(connection)

    return {"status": "ok"}
