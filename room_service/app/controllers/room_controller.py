from uuid import UUID

from fastapi import APIRouter

from app.dtos.room import CreateRoomDTO, JoinRoomDTO, RoomResponseDTO
from room_service.app.repositories.room_repository import RoomRepository
from room_service.app.services.room_service import RoomService

room_router = APIRouter(prefix="/rooms", tags=["Rooms"])


@room_router.post("", response_model=RoomResponseDTO)
def create_room(request_dto: CreateRoomDTO, host_id: UUID) -> RoomResponseDTO:
    room_repository = RoomRepository()
    room_service = RoomService(room_repository)
    return room_service.create_room_service(request_dto, host_id)


@room_router.get("/public", response_model=list[RoomResponseDTO])
def list_public_rooms() -> list[RoomResponseDTO]: ...


@room_router.get("/{room_code}", response_model=RoomResponseDTO)
def get_room(room_code: str, player_id: UUID) -> RoomResponseDTO: ...


@room_router.post("/{room_code}/join", response_model=RoomResponseDTO)
def join_room(
	room_code: str,
	request_dto: JoinRoomDTO,
	player_id: UUID,
) -> RoomResponseDTO: ...


@room_router.post("/{room_code}/leave", response_model=RoomResponseDTO)
def leave_room(room_code: str, player_id: UUID) -> RoomResponseDTO: ...


@room_router.post("/{room_code}/start", response_model=RoomResponseDTO)
def start_game(room_code: str, player_id: UUID) -> RoomResponseDTO: ...
