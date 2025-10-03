from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from nimbus.db import get_session
from nimbus.security.jwt import require_jwt
from nimbus.schemas.projects import (
    ProjectCreate, ProjectUpdate, ProjectOut, ProjectList, ProjectWithSecret
)
from nimbus.repositories.projects import (
    create_project, list_projects, get_project, update_project, rotate_project_key, delete_project
)

router = APIRouter(prefix="/v1/projects", tags=["projects"])


@router.post("", response_model=ProjectWithSecret, status_code=201, summary="Create a project")
async def create_project_endpoint(
    body: ProjectCreate,
    _claims: dict = Depends(require_jwt),
    session: AsyncSession = Depends(get_session),
):
    project, key_id, key_secret = await create_project(session, body.name)
    await session.commit()
    return {"project": project, "api_key_id": key_id, "api_key_secret": key_secret}


@router.get("", response_model=ProjectList, summary="List projects")
async def list_projects_endpoint(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    _claims: dict = Depends(require_jwt),
    session: AsyncSession = Depends(get_session),
):
    items, total = await list_projects(session, limit=limit, offset=offset)
    return {"items": items, "count": total}


@router.get("/{project_id}", response_model=ProjectOut, summary="Get a project")
async def get_project_endpoint(
    project_id: str,
    _claims: dict = Depends(require_jwt),
    session: AsyncSession = Depends(get_session),
):
    project = await get_project(session, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectOut, summary="Update a project")
async def update_project_endpoint(
    project_id: str,
    body: ProjectUpdate,
    _claims: dict = Depends(require_jwt),
    session: AsyncSession = Depends(get_session),
):
    project = await update_project(session, project_id, name=body.name)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    await session.commit()
    return project


@router.post("/{project_id}/rotate-key", response_model=ProjectWithSecret, summary="Rotate API key (returns new secret once)")
async def rotate_key_endpoint(
    project_id: str,
    _claims: dict = Depends(require_jwt),
    session: AsyncSession = Depends(get_session),
):
    result = await rotate_project_key(session, project_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    project, key_id, key_secret = result
    await session.commit()
    return {"project": project, "api_key_id": key_id, "api_key_secret": key_secret}


@router.delete("/{project_id}", status_code=204, summary="Delete a project")
async def delete_project_endpoint(
    project_id: str,
    _claims: dict = Depends(require_jwt),
    session: AsyncSession = Depends(get_session),
):
    ok = await delete_project(session, project_id)
    await session.commit()
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return
