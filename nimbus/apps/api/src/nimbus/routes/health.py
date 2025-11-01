from fastapi import APIRouter, HTTPException
from nimbus.db import check_database_health
from nimbus.cache import redis
import time
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])

@router.get("/health")
async def health():
    """Basic health check"""
    return {"status": "ok", "timestamp": int(time.time())}

@router.get("/health/detailed")
async def detailed_health():
    """Comprehensive health check including dependencies"""
    health_status = {
        "status": "ok",
        "timestamp": int(time.time()),
        "checks": {}
    }
    
    overall_healthy = True
    
    # Database health check
    try:
        db_healthy = await check_database_health()
        health_status["checks"]["database"] = {
            "status": "ok" if db_healthy else "error",
            "message": "Database connection successful" if db_healthy else "Database connection failed"
        }
        if not db_healthy:
            overall_healthy = False
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "error",
            "message": f"Database check failed: {str(e)}"
        }
        overall_healthy = False
    
    # Redis health check
    try:
        await redis.ping()
        health_status["checks"]["redis"] = {
            "status": "ok",
            "message": "Redis connection successful"
        }
    except Exception as e:
        health_status["checks"]["redis"] = {
            "status": "error",
            "message": f"Redis connection failed: {str(e)}"
        }
        overall_healthy = False
    
    # Update overall status
    health_status["status"] = "ok" if overall_healthy else "error"
    
    # Return appropriate HTTP status
    if not overall_healthy:
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status

@router.get("/healthz")
async def kubernetes_health():
    """Kubernetes-style health check (alias for /health)"""
    return await health()

@router.get("/readiness")
async def readiness():
    """Readiness probe for Kubernetes"""
    return await detailed_health()
