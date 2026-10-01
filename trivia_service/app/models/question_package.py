from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Integer, String, Text, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.question import Question


class QuestionPackage(Base):
    __tablename__ = "question_packages"
    __table_args__ = (UniqueConstraint("author_id", "name_key", name="uq_package_author_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    name_key: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    author_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    package_type: Mapped[str | None] = mapped_column(String(50))
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    questions: Mapped[list["Question"]] = relationship(
        back_populates="package",
        cascade="all, delete-orphan",
    )