from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.room import RoomStatus


class CreateRoomDTO(BaseModel):
	package_id: int = Field(gt=0)
	question_count: int = Field(ge=1)
	max_players: int = Field(ge=1)
	time_per_question: int = Field(ge=5)
	is_private: bool = False
	password: str | None = None
	show_ranking: bool = False


class UpdateRoomDTO(BaseModel):
	package_id: int | None = Field(default=None, gt=0)
	question_count: int | None = Field(default=None, ge=1)
	max_players: int | None = Field(default=None, ge=1)
	time_per_question: int | None = Field(default=None, ge=5)
	is_private: bool | None = None
	password: str | None = None
	show_ranking: bool | None = None


class JoinRoomDTO(BaseModel):
	password: str | None = None


class RoomResponseDTO(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
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
