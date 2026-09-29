from uuid import UUID, uuid4
from app.core.config import settings

from app.core.security import Security

from app.core.exceptions import RoomErrorMessage, RoomException
from app.dtos.room import CreateRoomDTO, JoinRoomDTO, RoomResponseDTO, DeleteRoomResponseDTO
from app.models.room import Room, RoomStatus
from app.repositories.room_repository import RoomRepository


class RoomService:
	def __init__(self, room_repository: RoomRepository) -> None: 
		self.room_repository = room_repository
		self.security = Security()

  
	def create_room_service(self, redis, request_dto: CreateRoomDTO, host_id: UUID) -> RoomResponseDTO:
		if host_id is None:
			raise RoomException(RoomErrorMessage.HOST_ID_REQUIRED)

		room_id = str(uuid4())
		
		room = Room(
			id=room_id,
			code="",
			host_id=host_id,
			players=[host_id],
		)
  
		configured_room = self.configure_room(room, request_dto)

		configured_room = self.room_repository.create_room(configured_room)
  
		return self.create_room_response_dto(configured_room)


	def get_room_service(self, room_code: str) -> RoomResponseDTO: 
		room = self.room_repository.get_room_by_code(room_code)
		if not room:
			raise RoomException(RoomErrorMessage.ROOM_NOT_FOUND)
		return self.create_room_response_dto(room)


	def list_public_rooms_service(self) -> list[RoomResponseDTO]:
		public_rooms = self.room_repository.list_public_rooms()
		return [self.create_room_response_dto(room) for room in public_rooms]
	
 
	def list_all_rooms_service(self) -> list[RoomResponseDTO]:
		public_rooms = self.room_repository.list_all_rooms()
		return [self.create_room_response_dto(room) for room in public_rooms]


	def change_room_service(
		self,
		room_code: str,
		request_dto: JoinRoomDTO,
		player_id: UUID,		
	) -> RoomResponseDTO:
		room = self.room_repository.get_room_by_code(room_code)
		is_host = self.identify_host(room, player_id)
	
		if not is_host:
			raise RoomException(RoomErrorMessage.HOST_ONLY)

		room = self.configure_room(room, request_dto)
		updated = self.room_repository.update_room_config(room)

		if not updated:
			raise RoomException(RoomErrorMessage.ROOM_UPDATE_FAILED)

		return self.create_room_response_dto(room)
  

	def join_room_service(
		self,
		room_code: str,
		request_dto: JoinRoomDTO,
		player_id: UUID,
	) -> RoomResponseDTO:
		room = self.room_repository.get_room_by_code(room_code)
		if not room:
			raise RoomException(RoomErrorMessage.ROOM_NOT_FOUND)

		if not self.validate_player_limit(room):
			raise RoomException(RoomErrorMessage.ROOM_FULL)

		if not self.validate_room_privacy(room, request_dto.password):
			raise RoomException(RoomErrorMessage.PRIVATE_ROOM_REQUIRED_PASSWORD)

		if player_id in room.players:
			raise RoomException(RoomErrorMessage.PLAYER_ALREADY_IN_ROOM)

		room.players.append(player_id)
		updated = self.room_repository.update_room_players(room)
		if not updated:
			raise RoomException(RoomErrorMessage.ROOM_UPDATE_FAILED)		
  
		return self.create_room_response_dto(room)

	def leave_room_service(self, room_code: str, player_id: UUID) -> RoomResponseDTO:
		room = self.room_repository.get_room_by_code(room_code)
		if not room:
			raise RoomException(RoomErrorMessage.ROOM_NOT_FOUND)

		if player_id not in room.players:
			raise RoomException(RoomErrorMessage.PLAYER_NOT_IN_ROOM)

		room.players.remove(player_id)
		updated = self.room_repository.update_room_players(room)
		if not updated:
			raise RoomException(RoomErrorMessage.ROOM_UPDATE_FAILED)  
  
		return self.create_room_response_dto(room)


	def start_game_service(self, room_code: str, player_id: UUID) -> RoomResponseDTO:
		self.host_can_start_game(room_code, player_id)

		room = self.update_room_status(room, RoomStatus.IN_PROGRESS)
		self.room_repository.update_room_status(room)
		return self.create_room_response_dto(room)


	def delete_room_service(self, room_code: str, player_id: UUID) -> DeleteRoomResponseDTO:
		room = self.room_repository.get_room_by_code(room_code)
		is_host = self.identify_host(room, player_id)

		if not is_host:
			raise RoomException(RoomErrorMessage.HOST_ONLY)

		deleted = self.room_repository.delete_room(room_code)
		if not deleted:
			raise RoomException(RoomErrorMessage.ROOM_NOT_FOUND)

		return DeleteRoomResponseDTO


	def configure_room(self, room: Room, request_dto: CreateRoomDTO) -> Room: 
		room.package_id = request_dto.package_id
		room.question_count = request_dto.question_count
		room.max_players = request_dto.max_players
		room.time_per_question = request_dto.time_per_question
		room.is_private = request_dto.is_private
		room.show_ranking = request_dto.show_ranking

		if room.is_private and not room.password: 
			if request_dto.password:
				room.password = self.security.hash_password(request_dto.password)
			else:
				raise RoomException(RoomErrorMessage.PRIVATE_ROOM_REQUIRED_PASSWORD)
	
		return room
  
  
	def identify_host(self, room: Room, player_id: UUID) -> bool:
		return room.host_id == player_id


	def validate_player_limit(self, room: Room) -> bool:
		return len(room.players) < room.max_players


	def validate_room_privacy(self, room: Room, room_password: str | None) -> bool: 
		if not room.is_private:
			return True

		return self.security.verify_password(room_password, room.password)
 
 
	def update_room_status(self, room: Room, status: RoomStatus) -> Room: 
		room.status = status
		return room


	def host_can_start_game(self, room_code: str, player_id: UUID) -> bool:
		room = self.room_repository.get_room_by_code(room_code)
		if not room:
			raise RoomException(RoomErrorMessage.ROOM_NOT_FOUND)

		if not self.identify_host(room, player_id):
			raise RoomException(RoomErrorMessage.ONLY_HOST_CAN_START_GAME)

		if len(room.players) < 1:
			raise RoomException(RoomErrorMessage.NOT_ENOUGH_PLAYERS)

		if room.status != RoomStatus.WAITING:
			raise RoomException(RoomErrorMessage.ROOM_ALREADY_STARTED)

		if len(room.players) > room.max_players:
			raise RoomException(RoomErrorMessage.ROOM_PLAYER_LIMIT_EXCEEDED)

		return True


	def create_room_response_dto(self, room: Room) -> RoomResponseDTO:
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
