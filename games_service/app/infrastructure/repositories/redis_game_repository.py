import json

from app.config import settings
from app.domain.entities.game import Game
from app.infrastructure.redis import get_redis_client


class RedisGameRepository:

    def __init__(self) -> None:
        self.redis = get_redis_client()

    async def save(self, game: Game) -> Game:
        game_key = f"game:{game.id}"
        room_game_key = f"game:room:{game.room_id}"

        if await self.redis.exists(game_key):
            raise ValueError(f"Game with ID {game.id} already exists.")

        await self.redis.hset(
            game_key,
            mapping=self._game_to_hash(game),
        )

        await self.redis.set(
            room_game_key,
            game.id,
        )

        await self.redis.expire(
            game_key,
            settings.game_ttl,
        )

        await self.redis.expire(
            room_game_key,
            settings.game_ttl,
        )

        return game

    async def get(self, game_id: str) -> Game | None:

        game_data = await self.redis.hgetall(
            f"game:{game_id}"
        )

        if not game_data:
            return None

        return self._hash_to_game(game_data)
    
    
    async def get_by_room_id(self, room_id: str) -> Game | None:
        game_id = await self.redis.get(
            f"game:room:{room_id}"
        )

        if not game_id:
            return None

        return await self.get(game_id)
    

    async def update(self, game: Game) -> bool:

        game_key = f"game:{game.id}"

        if not await self.redis.exists(game_key):
            return False

        await self.redis.hset(
            game_key,
            mapping=self._game_to_hash(game)
        )

        return True

    async def delete(self, game_id: str) -> bool:
        game = await self.get(game_id)

        if not game:
            return False

        deleted = await self.redis.delete(
            f"game:{game_id}",
            f"game:room:{game.room_id}",
        )

        return deleted > 0

    def _game_to_hash(self, game: Game) -> dict:

        return {
            "id": game.id,
            "room_id": game.room_id,
            "status": game.status,
            "current_question": json.dumps(
                game.current_question.model_dump()
                if game.current_question
                else None
            ),
            "questions": json.dumps([
                question.model_dump()
                for question in game.questions
            ]),
            "players": json.dumps([
                player.model_dump()
                for player in game.players
            ]),
            "question_time": game.question_time,
            "show_ranking": str(game.show_ranking),
        }

    def _hash_to_game(self, data: dict) -> Game:

        return Game.model_validate({
            "id": data["id"],
            "room_id": data["room_id"],
            "status": data["status"],
            "current_question": json.loads(
                data["current_question"]
            ),
            "questions": json.loads(
                data["questions"]
            ),
            "players": json.loads(
                data["players"]
            ),
            "question_time": int(
                data["question_time"]
            ),
            "show_ranking": data["show_ranking"] == "True",
        })