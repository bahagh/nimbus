from fastapi import APIRouter
import time
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])

@router.get("/health")
async def health():
    """Basic health check"""
    return {"status": "ok", "timestamp": int(time.time())}

@router.get("/healthz")
async def kubernetes_health():
    """Kubernetes-style health check (alias for /health)"""
    return await health()