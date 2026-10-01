from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class RoomStatus(StrEnum):
	WAITING = "WAITING"
	IN_PROGRESS = "IN_PROGRESS"
	FINISHED = "FINISHED"


class Room(BaseModel):
    id: UUID
    code: str
    host_id: UUID
    package_id: int | None = None
    question_count: int = 10
    max_players: int = 10
    time_per_question: int = 30
    is_private: bool = False
    show_ranking: bool = False
    status: RoomStatus = RoomStatus.WAITING
    players: list[UUID] = Field(default_factory=list)
    password: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
