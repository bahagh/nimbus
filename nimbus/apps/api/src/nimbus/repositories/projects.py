from __future__ import annotations

import hashlib
import secrets
import uuid
from typing import Optional, List, Dict

from sqlalchemy import select, func, update, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from nimbus.models.project import Project

# --- helpers ---------------------------------------------------------------

def _hash_secret(secret: str) -> bytes:
    # Store SHA-256(secret) binary
    return hashlib.sha256(secret.encode("utf-8")).digest()

def _new_key_id() -> str:
    # short-ish, url-safe
    return secrets.token_urlsafe(16)

def _new_key_secret() -> str:
    # longer, url-safe; only returned once
    return secrets.token_urlsafe(48)

# --- CRUD ------------------------------------------------------------------

async def create_project(session: AsyncSession, name: str) -> tuple[Dict, str, str]:
    from sqlalchemy import column
    from datetime import datetime
    
    api_key_id = _new_key_id()
    api_key_secret = _new_key_secret()
    api_key_hash = _hash_secret(api_key_secret)

    pid = uuid.uuid4()
    now = datetime.utcnow()
    
    stmt = insert(Project).values(
        id=pid,
        name=name,
        api_key_id=api_key_id,
        api_key_hash=api_key_hash,
    ).returning(
        column("id"),
        column("name"),
        column("api_key_id"),
        column("created_at"),
        column("updated_at")
    )
    res = await session.execute(stmt)
    row = res.one()

    out = {
        "id": str(row[0]),  # id
        "name": row[1],  # name
        "api_key_id": row[2],  # api_key_id
        "created_at": row[3],  # created_at
        "updated_at": row[4],  # updated_at
    }
    return out, api_key_id, api_key_secret

async def list_projects(session: AsyncSession, limit: int = 50, offset: int = 0) -> tuple[list[Dict], int]:
    total = (await session.execute(select(func.count()).select_from(Project))).scalar_one()
    stmt = (
        select(Project)
        .order_by(Project.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = (await session.execute(stmt)).scalars().all()
    items = [{
        "id": str(p.id),
        "name": p.name,
        "api_key_id": p.api_key_id,
        "created_at": p.created_at,
        "updated_at": p.updated_at,
    } for p in rows]
    return items, int(total)

async def get_project(session: AsyncSession, project_id: str) -> Optional[Dict]:
    stmt = select(Project).where(Project.id == uuid.UUID(project_id)).limit(1)
    obj = (await session.execute(stmt)).scalars().first()
    if not obj:
        return None
    return {
        "id": str(obj.id),
        "name": obj.name,
        "api_key_id": obj.api_key_id,
        "created_at": obj.created_at,
        "updated_at": obj.updated_at,
    }

async def update_project(session: AsyncSession, project_id: str, name: Optional[str]) -> Optional[Dict]:
    if name is None:
        return await get_project(session, project_id)

    stmt = (
        update(Project)
        .where(Project.id == uuid.UUID(project_id))
        .values(name=name)
        .returning(Project)
    )
    obj = (await session.execute(stmt)).scalars().first()
    if not obj:
        return None
    return {
        "id": str(obj.id),
        "name": obj.name,
        "api_key_id": obj.api_key_id,
        "created_at": obj.created_at,
        "updated_at": obj.updated_at,
    }

async def rotate_project_key(session: AsyncSession, project_id: str) -> Optional[tuple[Dict, str, str]]:
    api_key_id = _new_key_id()
    api_key_secret = _new_key_secret()
    api_key_hash = _hash_secret(api_key_secret)

    stmt = (
        update(Project)
        .where(Project.id == uuid.UUID(project_id))
        .values(api_key_id=api_key_id, api_key_hash=api_key_hash)
        .returning(Project)
    )
    obj = (await session.execute(stmt)).scalars().first()
    if not obj:
        return None
    out = {
        "id": str(obj.id),
        "name": obj.name,
        "api_key_id": obj.api_key_id,
        "created_at": obj.created_at,
        "updated_at": obj.updated_at,
    }
    return out, api_key_id, api_key_secret

async def delete_project(session: AsyncSession, project_id: str) -> bool:
    stmt = delete(Project).where(Project.id == uuid.UUID(project_id))
    res = await session.execute(stmt)
    return res.rowcount > 0
