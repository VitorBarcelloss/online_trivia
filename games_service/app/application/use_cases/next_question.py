from games_service.app.domain.repositories.game_repository import GameRepository


class NextQuestionUseCase:

    def __init__(
        self,
        game_repository: GameRepository
    ):
        self.game_repository = game_repository

    async def execute(self, game_id: str):

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

        current_index = next(
            (
                index
                for index, question in enumerate(game.questions)
                if question.id == game.current_question.id
            ),
            None
        )

        if current_index is None:
            raise ValueError(
                "Current question was not found in game."
            )

        next_index = current_index + 1

        if next_index >= len(game.questions):

            game.status = "FINISHED"

            await self.game_repository.update(game)

            return game

        game.current_question = game.questions[next_index]

        await self.game_repository.update(game)

        return game