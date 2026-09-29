from app.database.redis import get_redis_client
from app.core.config import settings
from app.models.room import Room
from app.core.exceptions import RoomErrorMessage, RoomException
from uuid import UUID
import json


class RoomRepository:
	def __init__(self) -> None:
		self.redis = get_redis_client()
  
	def create_room(self, room: Room) -> Room:
		while True:
			room_code = self.security.generate_room_code()
			
			success = self.redis.set(
				f"room:code:{room_code}",
				room.id,
				nx=True,
				ex=settings.room_ttl
			)

			if success:
				break

		self.redis.hset(
			f"room:{room.id}",
			mapping=self._room_to_hash(room),
		)
	
		self.redis.expire(
			f"room:{room.id}", 
			settings.room_ttl,
		)

		if room.is_public:
				self.redis.sadd("rooms:public", str(room.id))
  
		return room
		
  
	def get_room_by_code(self, room_code: str) -> Room | None:
		room_id = self.redis.get(f"room:code:{room_code}")
		if not room_id:
			raise RoomException(RoomErrorMessage.ROOM_NOT_FOUND)

		room_data = self.redis.hgetall(f"room:{room_id}")
		if not room_data:
			raise RoomException(RoomErrorMessage.ROOM_NOT_FOUND)

		return self._hash_to_room(room_data)


	def list_all_rooms(self) -> list[Room]:
		rooms = []
		for key in self.redis.scan_iter(match="room:*"):
			if key.startwith("room:code:"):
				continue
			
			data = self.redis.hgetall(key)
			if data:
				rooms.append(self._hash_to_room(data))
    
		return rooms

	def list_public_rooms(self) -> list[Room]:
		rooms = []
		room_ids = self.redis.smembers("rooms:public")
  
		for room_id in room_ids:
			data = self.redis.hgetall(f"room:{room_id}")
			if data:
				rooms.append(self._hash_to_room(data))

		return rooms

	def update_room_config(self, room: Room) -> bool:
		updated = self.redis.hset(
						f"room:{room.id}",
						mapping=self._room_to_hash(room)
						)

		return updated > 0

	def update_room_players(self, room: Room) -> bool:
		updated = self.redis.hset(
						f"room:{room.id}",
						"players",
						json.dumps([str(player) for player in room.players]),
						)
  
		return updated == 1

	def update_room_status(self, room: Room) -> Room:
		updated = self.redis.hset(
						f"room:{room.id}",
						"status",
						room.status,
						)
		
		return updated == 1

	def delete_room(self, room_code: str) -> bool:
		room_id = self.redis.get(f"room:code:{room_code}")
		if not room_id:
			return False

		deleted = self.redis.delete(
							f"room:{room_id}",
							f"room:code:{room_code}"
							)
		self.redis.srem("rooms:public", room_id)
  
		return deleted == 2
	
	def _hash_to_room(self, data: dict) -> Room:
		return Room(
			id=UUID(data["id"]),
			code=data["code"],
			host_id=UUID(data["host_id"]),
			package_id=UUID(data["package_id"]),
			status=data["status"],
			players=[
				UUID(player)
				for player in json.loads(data["players"])
			],
		)
  
	def _room_to_hash(self, room: Room) -> dict:
		return {
			"id": str(room.id),
			"code": room.code,
			"host_id": str(room.host_id),
			"package_id": str(room.package_id),
			"status": room.status.value,
			"players": json.dumps(
				[str(player) for player in room.players]
			),
		}