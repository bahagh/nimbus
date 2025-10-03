import datetime as dt
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class EventIn(BaseModel):
    name: str = Field(examples=["page_view"])
    ts: dt.datetime = Field(description="RFC3339/ISO8601", examples=["2024-01-01T12:00:00Z"])
    user_id: Optional[str] = Field(default=None, examples=["user-123"])
    seq: Optional[int] = Field(default=None, description="Monotonic per session (optional)")
    props: Dict[str, Any] = Field(default_factory=dict, examples=[{"k":"v"}])

class IngestRequest(BaseModel):
    project_id: str = Field(examples=["00000000-0000-0000-0000-000000000000"])
    events: List[EventIn]

class IngestResponse(BaseModel):
    accepted: int = Field(examples=[3])
class EventOut(BaseModel):
    id: str
    project_id: str
    name: str
    ts: str
    user_id: Optional[str] = None
    seq: Optional[int] = None
    props: Dict[str, Any]