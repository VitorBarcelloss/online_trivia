from datetime import datetime

from app.domain.entities.player_answer import PlayerAnswer
from app.domain.repositories.game_repository import GameRepository


class SubmitAnswerUseCase:

    def __init__(
        self,
        game_repository: GameRepository
    ):
        self.game_repository = game_repository

    async def execute(
        self,
        game_id: str,
        player_id: str,
        answer: str
    ) -> PlayerAnswer:

        game = await self.game_repository.get(game_id)

        if not game:
            raise ValueError(
                f"Game with ID {game_id} not found."
            )

        if game.status != "IN_PROGRESS":
            raise ValueError(
                "Game is not in progress."
            )

        if not game.current_question:
            raise ValueError(
                "There is no current question."
            )

        player = next(
            (
                player
                for player in game.players
                if player.user_id == player_id
            ),
            None
        )

        if not player:
            raise ValueError(
                "Player is not participating in this game."
            )

        already_answered = any(
            answer.player_id == player_id
            and answer.question_id == game.current_question.id
            for answer in game.answers
        )

        if already_answered:
            raise ValueError(
                "Player has already answered this question."
            )

        correct = answer == game.current_question.correct_answer

        player_answer = PlayerAnswer(
            player_id=player_id,
            question_id=game.current_question.id,
            answer=answer,
            answered_at=datetime.now(), #TODO rever o utcnow q ta deprecado
            correct=correct
        )

        game.answers.append(player_answer)

        await self.game_repository.update(game)

        return player_answer