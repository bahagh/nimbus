from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..cache import redis

router = APIRouter()


@router.websocket("/ws/projects/{project_id}")
async def ws_metrics(ws: WebSocket, project_id: str):
    await ws.accept()
    
    # Check if Redis is available
    if redis is None:
        await ws.send_json({"error": "WebSocket requires Redis (not configured)"})
        await ws.close()
        return
    
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"metrics:{project_id}")
    try:
        async for msg in pubsub.listen():
            if msg.get("type") == "message":
                await ws.send_text(msg["data"])
    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe(f"metrics:{project_id}")
