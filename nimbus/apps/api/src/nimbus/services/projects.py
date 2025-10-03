from sqlalchemy.ext.asyncio import AsyncSession
from nimbus.repositories.projects import (
    list_projects, get_project, create_project, rotate_project_key
)
import uuid

async def svc_list_projects(session: AsyncSession):
    return await list_projects(session)

async def svc_get_project(session: AsyncSession, project_id: str):
    return await get_project(session, uuid.UUID(project_id))

async def svc_create_project(session: AsyncSession, name: str):
    return await create_project(session, name)

async def svc_rotate_key(session: AsyncSession, project_id: str):
    return await rotate_project_key(session, uuid.UUID(project_id))
