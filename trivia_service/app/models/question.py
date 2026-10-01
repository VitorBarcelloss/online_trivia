from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.alternative import Alternative
    from app.models.question_package import QuestionPackage


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (UniqueConstraint("package_id", "statement", name="uq_question_package_statement"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    package_id: Mapped[int] = mapped_column(
        ForeignKey("question_packages.id"),
        nullable=False,
    )
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    package: Mapped["QuestionPackage"] = relationship(back_populates="questions")
    alternatives: Mapped[list["Alternative"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
    )