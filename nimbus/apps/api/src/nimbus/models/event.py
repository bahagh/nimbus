import datetime as dt
import uuid
from typing import Optional, Dict, Any
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, JSON, Integer, ForeignKey, DateTime
from nimbus.models.base import Base, UUIDMixin, Timestamped

class Event(Base, UUIDMixin, Timestamped):
    __tablename__ = "events"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    ts: Mapped[dt.datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    props: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    seq: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    # NOTE: idempotency_key column doesn't exist yet in database (migration pending)
    # idempotency_key: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    __table_args__ = {"extend_existing": True}
