from app.database.base import Base

from sqlalchemy import Date, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from datetime import date, datetime
import uuid
from uuid import UUID


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    
    nickname: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )
    
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    
    phone: Mapped[str | None] = mapped_column(
        String(25),
        nullable=True,
    )
    
    birth_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    ) 
    
    country: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )