
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

class RoomStatus(StrEnum):
	WAITING = "WAITING"
	IN_PROGRESS = "IN_PROGRESS"
	FINISHED = "FINISHED"


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
