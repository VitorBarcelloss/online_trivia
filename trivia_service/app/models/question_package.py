from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, Date, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.question import Question


class QuestionPackage(Base):
    __tablename__ = "question_packages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text)
    author_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    package_type: Mapped[str | None] = mapped_column(String(50))
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[date | None] = mapped_column(Date)
    updated_at: Mapped[date | None] = mapped_column(Date)

    questions: Mapped[list["Question"]] = relationship(
        back_populates="package",
        cascade="all, delete-orphan",
    )