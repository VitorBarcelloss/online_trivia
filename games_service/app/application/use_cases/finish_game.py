
from app.domain.repositories.game_repository import GameRepository


class FinishGameUseCase:

    def __init__(
        self,
        game_repository: GameRepository
    ):
        self.game_repository = game_repository

    async def execute(
        self,
        game_id: str,
        player_id: str
    ):

        game = await self.game_repository.get(game_id)

        if not game:
            raise ValueError(
                f"Game with ID {game_id} not found."
            )

        if game.status == "FINISHED":
            return game

        if game.host_id != player_id:
            raise ValueError(
                "Only the host can finish the game."
            )

        game.status = "FINISHED"

        await self.game_repository.update(game)

        return game