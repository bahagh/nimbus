import uuid
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from nimbus.settings import settings
from nimbus.routes import health, auth, events, metrics
from nimbus.routes import projects

# Setup logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address) if settings.rate_limit_enabled else None

app = FastAPI(
    title=settings.app_name,
    version="0.1.0-beta.1",
    description="Open-source event analytics API - Alternative to Segment & Mixpanel",
    contact={
        "name": "Nimbus",
        "url": "https://github.com/bahagh/nimbus",
        "email": "baha.ghrissi@esprit.tn"
    },
    license_info={
        "name": "MIT",
        "url": "https://github.com/bahagh/nimbus/blob/master/LICENSE",
    },
    debug=settings.debug,
)

# Add rate limiter to app state
if limiter:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Global exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = str(uuid.uuid4())
    logger.error(
        f"Unhandled exception: {exc}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "client_ip": request.client.host if request.client else None,
        },
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "request_id": request_id
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "details": exc.errors(),
            "path": request.url.path
        }
    )

@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    request_id = str(uuid.uuid4())
    logger.error(
        f"Database error: {exc}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
        },
        exc_info=True
    )
    return JSONResponse(
        status_code=503,
        content={
            "error": "Database error",
            "message": "A database error occurred",
            "request_id": request_id
        }
    )

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(metrics.router)
app.include_router(projects.router)
