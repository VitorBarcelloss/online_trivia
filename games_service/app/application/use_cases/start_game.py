import random
import uuid

from app.infrastructure.clients.room_client import RoomClient
from app.infrastructure.clients.trivia_client import TriviaClient

from games_service.app.domain.entities.game import Game
from games_service.app.domain.entities.game_player import GamePlayer
from games_service.app.domain.repositories.game_repository import GameRepository


class StartGameUseCase:

    def __init__(
        self,
        room_client: RoomClient,
        trivia_client: TriviaClient,
        game_repository: GameRepository,
    ):
        self.room_client = room_client
        self.trivia_client = trivia_client
        self.game_repository = game_repository

    async def execute(
        self,
        room_code: str,
        player_id: uuid.UUID,
    ) -> Game:

        room = await self.room_client.start_room_game(
            room_code=room_code,
            player_id=player_id,
        )

        if not room:
            raise ValueError(
                "Room not found."
            )

        existing_game = await self.game_repository.get_by_room_id(
            str(room.id)
        )

        if existing_game:
            raise ValueError(
                "A game already exists for this room."
            )

        questions = await self.trivia_client.get_questions(
            room.package_id
        )

        if not questions:
            raise ValueError(
                f"No questions found for package ID "
                f"{room.package_id}."
            )

        if len(questions) < room.question_count:
            raise ValueError(
                "Not enough questions available for "
                "the requested count. "
                f"Available: {len(questions)}, "
                f"Requested: {room.question_count}."
            )

        selected_questions = random.sample(
            questions,
            k=room.question_count,
        )

        players = [
            GamePlayer(
                user_id=str(player_id),
                nickname=str(player_id),
                score=0,
            )
            for player_id in room.players
        ]

        game = Game(
            id=str(uuid.uuid4()),
            room_id=str(room.id),
            host_id=str(room.host_id),
            status="IN_PROGRESS",
            current_question=selected_questions[0],
            questions=selected_questions,
            players=players,
            question_time=room.time_per_question,
            show_ranking=room.show_ranking,
        )

        await self.game_repository.save(game)

        return game
