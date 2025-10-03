import datetime as dt
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class EventOut(BaseModel):
    id: str
    project_id: str
    name: str
    ts: str
    props: Dict[str, Any] = Field(default_factory=dict)
    user_id: Optional[str] = None
    seq: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class EventsPage(BaseModel):
    items: List[EventOut]
    limit: int
    offset: int
