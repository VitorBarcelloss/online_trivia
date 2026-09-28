from uuid import UUID

from pydantic import BaseModel, Field

from app.models.room import RoomStatus


class CreateRoomDTO(BaseModel):
	package_id: int
	question_count: int = Field(ge=1)
	max_players: int = Field(ge=1)
	time_per_question: int = Field(ge=5)
	is_private: bool = False
	password: str | None = None
	show_ranking: bool = False


class JoinRoomDTO(BaseModel):
	nickname: str
	password: str | None = None


class RoomResponseDTO(BaseModel):
	code: str
	host_id: UUID
	package_id: int
	question_count: int
	max_players: int
	time_per_question: int
	is_private: bool
	show_ranking: bool
	status: RoomStatus
	players: list[UUID]
