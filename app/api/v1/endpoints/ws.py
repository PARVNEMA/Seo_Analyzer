from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List, Any
import json
from app.services.crawler_service import stop_crawl_process

router = APIRouter()

# Store active websocket connections per job_id
# job_id -> list of active connections
active_connections: Dict[str, List[WebSocket]] = {}

@router.websocket("/ws/crawls/{job_id}")
async def crawl_websocket(websocket: WebSocket, job_id: str):
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
async def crawl_webhook(job_id: str, data: Dict[str, Any]):
    """
    Webhook endpoint for the Scrapy pipeline to post real-time updates.
    These updates are saved to Supabase and broadcasted to WebSockets.
    """
    from app.db.supabase import get_supabase_client
    
    # Save to Supabase
    try:
        supabase = get_supabase_client()
        supabase.table("crawl_results").insert(data).execute()
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
