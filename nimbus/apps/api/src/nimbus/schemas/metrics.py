from typing import List
from pydantic import BaseModel, Field

class SeriesPoint(BaseModel):
    ts: str = Field(examples=["2024-01-01T12:00:00Z"])
    value: float = Field(examples=[42])

class MetricsResponse(BaseModel):
    metric: str = Field(examples=["events.count"])
    bucket: str = Field(examples=["1h"])
    series: List[SeriesPoint]
