from uuid import UUID

from fastapi import APIRouter

from app.dtos.room import CreateRoomDTO, JoinRoomDTO, RoomResponseDTO, DeleteRoomResponseDTO
from room_service.app.repositories.room_repository import RoomRepository
from room_service.app.services.room_service import RoomService

room_router = APIRouter(prefix="/rooms", tags=["Rooms"])


@room_router.post("", response_model=RoomResponseDTO)
def create_room(request_dto: CreateRoomDTO, host_id: UUID) -> RoomResponseDTO:
    room_repository = RoomRepository()
    room_service = RoomService(room_repository)
    return room_service.create_room_service(request_dto, host_id)

@room_router.get("/public", response_model=list[RoomResponseDTO])
def list_public_rooms() -> list[RoomResponseDTO]: 
    room_repository = RoomRepository()
    room_service = RoomService(room_repository)
    return room_service.list_public_rooms_service()

@room_router.get("/all", response_model=list[RoomResponseDTO])
def list_all_rooms() -> list[RoomResponseDTO]:
    room_repository = RoomRepository()
    room_service = RoomService(room_repository)
    return room_service.list_all_rooms_service()

@room_router.get("/{room_code}", response_model=RoomResponseDTO)
def get_room(room_code: str) -> RoomResponseDTO:
    room_repository = RoomRepository()
    room_service = RoomService(room_repository)
    return room_service.get_room_service(room_code)

@room_router.put("/{room_code}/change", response_model=RoomResponseDTO)
def change_room(
    room_code: str,
    request_dto: CreateRoomDTO,
    player_id: UUID,
) -> RoomResponseDTO:
    room_repository = RoomRepository()
    room_service = RoomService(room_repository)
    return room_service.change_room_service(room_code, request_dto, player_id)

@room_router.put("/{room_code}/join", response_model=RoomResponseDTO)
def join_room(
	room_code: str,
	request_dto: JoinRoomDTO,
	player_id: UUID,
) -> RoomResponseDTO:
    room_repository = RoomRepository()
    room_service = RoomService(room_repository)
    return room_service.join_room_service(room_code, request_dto, player_id)

@room_router.put("/{room_code}/leave", response_model=RoomResponseDTO)
def leave_room(room_code: str, player_id: UUID) -> RoomResponseDTO:
    room_repository = RoomRepository()
    room_service = RoomService(room_repository)
    return room_service.leave_room_service(room_code, player_id)

@room_router.delete("/{room_code}", response_model=DeleteRoomResponseDTO)
def delete_room(room_code: str, player_id: UUID) -> DeleteRoomResponseDTO:
    room_repository = RoomRepository()
    room_service = RoomService(room_repository)
    return room_service.delete_room_service(room_code, player_id)

@room_router.post("/{room_code}/start", response_model=RoomResponseDTO)
def start_game(room_code: str, player_id: UUID) -> RoomResponseDTO: 
    room_repository = RoomRepository()
    room_service = RoomService(room_repository)
    return room_service.start_game_service(room_code, player_id)
