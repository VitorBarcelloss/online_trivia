import asyncio
import json
from datetime import datetime
from uuid import UUID

from app.core.config import settings
from app.database.redis import get_redis_client
from app.core.exceptions import RoomErrorMessage, RoomException
from app.models.room import Room, RoomStatus
from app.core.security import Security


class RoomRepository:
	def __init__(self) -> None:
		self.redis = get_redis_client()
		self.security = Security()

	async def create_room(
		self,
		room: Room,
		idempotency_key: str | None = None,
		request_fingerprint: str | None = None,
	) -> Room | None:
		redis_idempotency_key = None
  
		if idempotency_key:
			key = f"room:idempotency:{room.host_id}:{idempotency_key}"
			stored = await self.redis.get(key)
   
			if stored:
				return await self._room_for_retry(stored, request_fingerprint)

			reservation = json.dumps({
				"fingerprint": request_fingerprint,
				"room_id": "",
				"host_id": str(room.host_id),
				"key": idempotency_key,
			})
   
			reserved = await self.redis.set(
				key,
				reservation,
				nx=True,
				ex=settings.room_ttl,
			)
   
			if not reserved:
				stored = await self.redis.get(key)
    
				if stored:
					return await self._room_for_retry(stored, request_fingerprint)
 
				raise RoomException(RoomErrorMessage.IDEMPOTENCY_KEY_CONFLICT)

			redis_idempotency_key = key

		for _ in range(20):
			room_code = self.security.generate_room_code()
			reserved = await self.redis.set(
				f"room:code:{room_code}",
				str(room.id),
				nx=True,
				ex=settings.room_ttl,
			)
   
			if reserved:
				room.code = room_code
				break
		else:
			if redis_idempotency_key:
				await self.redis.delete(redis_idempotency_key)
			return None

		await self.redis.hset(f"room:{room.id}", mapping=self._room_to_hash(room))
		await self.redis.expire(f"room:{room.id}", settings.room_ttl)
  
		if redis_idempotency_key:
			await self.redis.set(
				redis_idempotency_key,
				json.dumps({"fingerprint": request_fingerprint, "room_id": str(room.id)}),
				ex=settings.room_ttl,
			)
   
		if not room.is_private:
			await self.redis.sadd("rooms:public", str(room.id))
   
		return room

	async def _room_for_retry(self, stored: str, request_fingerprint: str | None) -> Room:
		data = json.loads(stored)
  
		for _ in range(40):
			if data.get("fingerprint") != request_fingerprint:
				raise RoomException(RoomErrorMessage.IDEMPOTENCY_KEY_CONFLICT)

			if data.get("room_id"):
				room_hash = await self.redis.hgetall(f"room:{data['room_id']}")
				if room_hash:
					return self._hash_to_room(room_hash)
				break

			await asyncio.sleep(0.05)
   
			key = f"room:idempotency:{data.get('host_id', '')}:{data.get('key', '')}"
			stored = await self.redis.get(key) or stored
			data = json.loads(stored)
   
		raise RoomException(RoomErrorMessage.IDEMPOTENCY_KEY_CONFLICT)

	async def get_room_by_code(self, room_code: str) -> Room | None:
		room_id = await self.redis.get(f"room:code:{room_code}")
  
		if not room_id:
			return None

		room_data = await self.redis.hgetall(f"room:{room_id}")
		return self._hash_to_room(room_data) if room_data else None

	async def list_all_rooms(self) -> list[Room]:
		rooms = []
  
		async for key in self.redis.scan_iter(match="room:*"):
			if key.startswith("room:code:"):
				continue

			data = await self.redis.hgetall(key)
			if data:
				rooms.append(self._hash_to_room(data))
    
		return rooms

	async def list_public_rooms(self) -> list[Room]:
		rooms = []
  
		for room_id in await self.redis.smembers("rooms:public"):
			data = await self.redis.hgetall(f"room:{room_id}")
			if data:
				rooms.append(self._hash_to_room(data))
    
		return rooms

	async def update_room(self, room: Room) -> bool:
		key = f"room:{room.id}"
  
		if not await self.redis.exists(key):
			return False

		await self.redis.hset(key, mapping=self._room_to_hash(room))
  
		if room.is_private:
			await self.redis.srem("rooms:public", str(room.id))
		else:
			await self.redis.sadd("rooms:public", str(room.id))
   
		return True

	async def delete_room(self, room_code: str) -> bool:
		room_id = await self.redis.get(f"room:code:{room_code}")
  
		if not room_id:
			return True

		await self.redis.delete(f"room:{room_id}", f"room:code:{room_code}")
		await self.redis.srem("rooms:public", room_id)
  
		return True

	@staticmethod
	def _hash_to_room(data: dict[str, str]) -> Room:
		return Room(
			id=UUID(data["id"]),
			code=data["code"],
			host_id=UUID(data["host_id"]),
			package_id=int(data["package_id"]),
			question_count=int(data["question_count"]),
			max_players=int(data["max_players"]),
			time_per_question=int(data["time_per_question"]),
			is_private=data["is_private"] == "true",
			show_ranking=data["show_ranking"] == "true",
			status=RoomStatus(data["status"]),
			players=[UUID(player) for player in json.loads(data["players"])],
			password=data.get("password") or None,
			created_at=datetime.fromisoformat(data["created_at"]),
		)

	@staticmethod
	def _room_to_hash(room: Room) -> dict[str, str]:
		return {
			"id": str(room.id),
			"code": room.code,
			"host_id": str(room.host_id),
			"package_id": str(room.package_id),
			"question_count": str(room.question_count),
			"max_players": str(room.max_players),
			"time_per_question": str(room.time_per_question),
			"is_private": str(room.is_private).lower(),
			"show_ranking": str(room.show_ranking).lower(),
			"status": room.status.value,
			"players": json.dumps([str(player) for player in room.players]),
			"password": room.password or "",
			"created_at": room.created_at.isoformat(),
		}