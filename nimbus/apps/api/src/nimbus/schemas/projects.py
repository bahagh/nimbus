from __future__ import annotations
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200, examples=["My Product"])

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200, examples=["New Name"])

class ProjectOut(BaseModel):
    id: str
    name: str
    api_key_id: str
    created_at: datetime
    updated_at: datetime

class ProjectList(BaseModel):
    items: List[ProjectOut]
    count: int

class ProjectWithSecret(BaseModel):
    """Returned only on create/rotate. Shows the plaintext secret once."""
    project: ProjectOut
    api_key_id: str
    api_key_secret: str
