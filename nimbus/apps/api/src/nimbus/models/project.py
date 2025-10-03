import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, LargeBinary
from nimbus.models.base import Base, UUIDMixin, Timestamped

class Project(Base, UUIDMixin, Timestamped):
    __tablename__ = "projects"
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    api_key_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    api_key_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
