from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, Timestamped, UUIDMixin



from sqlalchemy import LargeBinary

class User(Base, UUIDMixin, Timestamped):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    hashed_password: Mapped[bytes] = mapped_column(LargeBinary)
