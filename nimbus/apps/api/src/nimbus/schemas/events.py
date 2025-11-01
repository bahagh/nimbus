from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class IngestEvent(BaseModel):
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=200,
        pattern=r'^[a-zA-Z0-9_.-]+$',
        description="Event name - alphanumeric, underscore, dot, dash only"
    )
    ts: datetime = Field(..., description="Event timestamp in ISO 8601 format")
    user_id: Optional[str] = Field(
        None, 
        max_length=200,
        description="User identifier"
    )
    props: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Event properties",
        examples=[{"plan": "pro", "feature": "analytics"}]
    )
    idempotency_key: Optional[str] = Field(
        None,
        max_length=64,
        pattern=r'^[a-zA-Z0-9_-]+$',
        description="Idempotency key for deduplication"
    )

    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Event name cannot be empty')
        
        # Sanitize name
        sanitized = re.sub(r'[^a-zA-Z0-9_.-]', '', v.strip())
        if not sanitized:
            raise ValueError('Event name contains only invalid characters')
        
        return sanitized

    @validator('props')
    def validate_props(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Properties must be a dictionary')
        
        # Limit nested depth
        def check_depth(obj, depth=0):
            if depth > 5:
                raise ValueError('Properties nested too deeply (max 5 levels)')
            if isinstance(obj, dict):
                for value in obj.values():
                    check_depth(value, depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    check_depth(item, depth + 1)
        
        check_depth(v)
        
        # Limit size when serialized
        import json
        serialized = json.dumps(v)
        if len(serialized) > 10000:  # 10KB limit
            raise ValueError('Properties too large (max 10KB when serialized)')
        
        return v

    @validator('user_id')
    def validate_user_id(cls, v):
        if v is not None:
            # Remove potentially dangerous characters
            sanitized = re.sub(r'[<>"\']', '', v.strip())
            return sanitized if sanitized else None
        return v


class IngestRequest(BaseModel):
    project_id: str = Field(
        ...,
        pattern=r'^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
        description="Project UUID"
    )
    events: List[IngestEvent] = Field(
        ...,
        min_items=1,
        max_items=1000,
        description="List of events to ingest (max 1000 per request)"
    )

    @validator('events')
    def validate_events_batch_size(cls, v):
        if len(v) > 1000:
            raise ValueError('Too many events in batch (max 1000)')
        return v


class IngestResponse(BaseModel):
    accepted: int = Field(..., description="Number of events successfully accepted")
    rejected: int = Field(default=0, description="Number of events rejected")
    errors: List[str] = Field(default_factory=list, description="List of errors if any")
