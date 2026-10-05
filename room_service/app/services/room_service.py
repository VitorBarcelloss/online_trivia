import hashlib
import json
from uuid import UUID, uuid4

from app.core.exceptions import RoomErrorMessage, RoomException
from app.core.security import Security
from app.dtos.room import (
    CreateRoomDTO,
    JoinRoomDTO,
    RoomResponseDTO,
    UpdateRoomDTO,
)
from app.models.room import Room, RoomStatus
from app.repositories.room_repository import RoomRepository
from app.infrastructure.messaging.rabbitmq_publisher import (
    publish_player_joined,
    publish_player_left,
)


class RoomService:

    def __init__(
        self,
        room_repository: RoomRepository,
    ) -> None:
        self.room_repository = room_repository
        self.security = Security()

    async def create_room_service(
        self,
        request_dto: CreateRoomDTO,
        host_id: UUID,
        idempotency_key: str | None = None,
    ) -> RoomResponseDTO:

        room = Room(
            id=uuid4(),
            code="",
            host_id=host_id,
            players=[host_id],
        )

        self.configure_room(
            room,
            request_dto,
        )

        fingerprint = None

        if idempotency_key is not None:
            if (
                not idempotency_key.strip()
                or len(idempotency_key) > 128
            ):
                raise RoomException(
                    RoomErrorMessage.INVALID_REQUEST
                )

            payload = json.dumps(
                request_dto.model_dump(
                    mode="json"
                ),
                sort_keys=True,
                separators=(",", ":"),
            )

            fingerprint = hashlib.sha256(
                payload.encode()
            ).hexdigest()

        created = await self.room_repository.create_room(
            room,
            idempotency_key,
            fingerprint,
        )

        if created is None:
            raise RoomException(
                RoomErrorMessage.ROOM_CODE_GENERATION_FAILED
            )

        return self.create_room_response_dto(created)

    async def get_room_service(
        self,
        room_code: str,
    ) -> RoomResponseDTO:

        room = await self.require_room(room_code)

        return self.create_room_response_dto(room)

    async def list_public_rooms_service(
        self,
    ) -> list[RoomResponseDTO]:

        rooms = await self.room_repository.list_public_rooms()

        return [
            self.create_room_response_dto(room)
            for room in rooms
        ]

    async def list_all_rooms_service(
        self,
    ) -> list[RoomResponseDTO]:

        rooms = await self.room_repository.list_all_rooms()

        return [
            self.create_room_response_dto(room)
            for room in rooms
        ]

    async def change_room_service(
        self,
        room_code: str,
        request_dto: UpdateRoomDTO,
        player_id: UUID,
    ) -> RoomResponseDTO:

        room = await self.require_room(room_code)

        self.require_host(
            room,
            player_id,
        )

        self.update_room_config(
            room,
            request_dto,
        )

        if not await self.room_repository.update_room(room):
            raise RoomException(
                RoomErrorMessage.ROOM_UPDATE_FAILED
            )

        return self.create_room_response_dto(room)

    async def join_room_service(
        self,
        room_code: str,
        request_dto: JoinRoomDTO,
        player_id: UUID,
    ) -> RoomResponseDTO:

        room = await self.require_room(room_code)

        if player_id in room.players:
            return self.create_room_response_dto(room)

        if room.status != RoomStatus.WAITING:
            raise RoomException(
                RoomErrorMessage.ROOM_NOT_WAITING
            )

        if len(room.players) >= room.max_players:
            raise RoomException(
                RoomErrorMessage.ROOM_FULL
            )

        if not self.validate_room_privacy(
            room,
            request_dto.password,
        ):
            raise RoomException(
                RoomErrorMessage.PRIVATE_ROOM_REQUIRED_PASSWORD
            )

        room.players.append(player_id)

        if not await self.room_repository.update_room(room):
            raise RoomException(
                RoomErrorMessage.ROOM_UPDATE_FAILED
            )

        await publish_player_joined(
            room_code=room.code,
            player_id=str(player_id),
        )

        return self.create_room_response_dto(room)

    async def leave_room_service(
        self,
        room_code: str,
        player_id: UUID,
    ) -> None:

        room = await self.room_repository.get_room_by_code(
            room_code
        )

        if room is None or player_id not in room.players:
            return

        room.players.remove(player_id)

        if not await self.room_repository.update_room(room):
            raise RoomException(
                RoomErrorMessage.ROOM_UPDATE_FAILED
            )

        await publish_player_left(
            room_code=room.code,
            player_id=str(player_id),
        )

    async def start_game_service(
        self,
        room_code: str,
        player_id: UUID,
    ) -> RoomResponseDTO:

        room = await self.require_room(room_code)

        self.require_host(
            room,
            player_id,
        )

        if room.status == RoomStatus.IN_PROGRESS:
            return self.create_room_response_dto(room)

        if room.status != RoomStatus.WAITING:
            raise RoomException(
                RoomErrorMessage.ROOM_ALREADY_STARTED
            )

        if not room.players:
            raise RoomException(
                RoomErrorMessage.NOT_ENOUGH_PLAYERS
            )

        room.status = RoomStatus.IN_PROGRESS

        if not await self.room_repository.update_room(room):
            raise RoomException(
                RoomErrorMessage.ROOM_UPDATE_FAILED
            )

        return self.create_room_response_dto(room)

    async def delete_room_service(
        self,
        room_code: str,
        player_id: UUID,
    ) -> None:

        room = await self.room_repository.get_room_by_code(
            room_code
        )

        if room is not None:
            self.require_host(
                room,
                player_id,
            )

            await self.room_repository.delete_room(
                room_code
            )

    async def require_room(
        self,
        room_code: str,
    ) -> Room:

        room = await self.room_repository.get_room_by_code(
            room_code
        )

        if room is None:
            raise RoomException(
                RoomErrorMessage.ROOM_NOT_FOUND
            )

        return room

    @staticmethod
    def require_host(
        room: Room,
        player_id: UUID,
    ) -> None:

        if room.host_id != player_id:
            raise RoomException(
                RoomErrorMessage.HOST_ONLY
            )

    def configure_room(
        self,
        room: Room,
        request_dto: CreateRoomDTO,
    ) -> None:

        room.package_id = request_dto.package_id
        room.question_count = request_dto.question_count
        room.max_players = request_dto.max_players
        room.time_per_question = request_dto.time_per_question
        room.is_private = request_dto.is_private
        room.show_ranking = request_dto.show_ranking

        if room.is_private:
            if not request_dto.password:
                raise RoomException(
                    RoomErrorMessage.PRIVATE_ROOM_REQUIRED_PASSWORD
                )

            room.password = self.security.hash_password(
                request_dto.password
            )

    def update_room_config(
        self,
        room: Room,
        request_dto: UpdateRoomDTO,
    ) -> None:

        changes = request_dto.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )

        for field, value in changes.items():
            if field == "password":
                continue

            setattr(
                room,
                field,
                value,
            )

        if room.is_private:
            if request_dto.password:
                if (
                    not room.password
                    or not self.security.verify_password(
                        request_dto.password,
                        room.password,
                    )
                ):
                    room.password = self.security.hash_password(
                        request_dto.password
                    )

            elif not room.password:
                raise RoomException(
                    RoomErrorMessage.PRIVATE_ROOM_REQUIRED_PASSWORD
                )

        else:
            room.password = None

    def validate_room_privacy(
        self,
        room: Room,
        room_password: str | None,
    ) -> bool:

        if not room.is_private:
            return True

        if not room_password or not room.password:
            return False

        return self.security.verify_password(
            room_password,
            room.password,
        )

    @staticmethod
    def create_room_response_dto(
        room: Room,
    ) -> RoomResponseDTO:

        return RoomResponseDTO(
            id=room.id,
            code=room.code,
            host_id=room.host_id,
            package_id=room.package_id,
            question_count=room.question_count,
            max_players=room.max_players,
            time_per_question=room.time_per_question,
            is_private=room.is_private,
            show_ranking=room.show_ranking,
            status=room.status,
            players=room.players,
        )

