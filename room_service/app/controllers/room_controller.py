from uuid import UUID

from fastapi import APIRouter, Header, Response, status

from app.dtos.room import CreateRoomDTO, JoinRoomDTO, RoomResponseDTO, UpdateRoomDTO
from app.repositories.room_repository import RoomRepository
from app.services.room_service import RoomService

room_router = APIRouter(prefix="/rooms", tags=["Rooms"])


@room_router.post("", response_model=RoomResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_room(
	request_dto: CreateRoomDTO,
	host_id: UUID,
	idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> RoomResponseDTO:
    room_repository = RoomRepository()
    room_service = RoomService(room_repository)
    return await room_service.create_room_service(request_dto, host_id, idempotency_key)

@room_router.get("", response_model=list[RoomResponseDTO])
async def list_public_rooms() -> list[RoomResponseDTO]:
    room_repository = RoomRepository()
    room_service = RoomService(room_repository)
    return await room_service.list_public_rooms_service()

@room_router.get("/all", response_model=list[RoomResponseDTO])
async def list_all_rooms() -> list[RoomResponseDTO]:
    room_repository = RoomRepository()
    room_service = RoomService(room_repository)
    return await room_service.list_all_rooms_service()

@room_router.get("/{room_code}", response_model=RoomResponseDTO)
async def get_room(room_code: str) -> RoomResponseDTO:
    room_repository = RoomRepository()
    room_service = RoomService(room_repository)
    return await room_service.get_room_service(room_code)

@room_router.patch("/{room_code}", response_model=RoomResponseDTO)
async def change_room(
    room_code: str,
    request_dto: UpdateRoomDTO,
    player_id: UUID,
) -> RoomResponseDTO:
    room_repository = RoomRepository()
    room_service = RoomService(room_repository)
    return await room_service.change_room_service(room_code, request_dto, player_id)

@room_router.post("/{room_code}/players", response_model=RoomResponseDTO)
async def join_room(
	room_code: str,
	request_dto: JoinRoomDTO,
	player_id: UUID,
) -> RoomResponseDTO:
    room_repository = RoomRepository()
    room_service = RoomService(room_repository)
    return await room_service.join_room_service(room_code, request_dto, player_id)

@room_router.delete("/{room_code}/players/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def leave_room(room_code: str, player_id: UUID) -> Response:
    room_repository = RoomRepository()
    room_service = RoomService(room_repository)
    await room_service.leave_room_service(room_code, player_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@room_router.delete("/{room_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(room_code: str, player_id: UUID) -> Response:
    room_repository = RoomRepository()
    room_service = RoomService(room_repository)
    await room_service.delete_room_service(room_code, player_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@room_router.post("/{room_code}/start", response_model=RoomResponseDTO)
async def start_game(room_code: str, player_id: UUID) -> RoomResponseDTO:
    room_repository = RoomRepository()
    room_service = RoomService(room_repository)
    return await room_service.start_game_service(room_code, player_id)
