from fastapi import APIRouter, WebSocket

from ..cache import redis

router = APIRouter()


@router.websocket("/ws/projects/{project_id}")
async def ws_metrics(ws: WebSocket, project_id: str):
    await ws.accept()
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"metrics:{project_id}")
    try:
        async for msg in pubsub.listen():
            if msg.get("type") == "message":
                await ws.send_text(msg["data"])
    finally:
        await pubsub.unsubscribe(f"metrics:{project_id}")
