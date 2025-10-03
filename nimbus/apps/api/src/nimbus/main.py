from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from nimbus.settings import settings
from nimbus.routes import health, auth, events, metrics
from nimbus.routes import projects

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Nimbus API for event ingestion and metrics",
    contact={"name": "Nimbus"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(metrics.router)
app.include_router(projects.router)
