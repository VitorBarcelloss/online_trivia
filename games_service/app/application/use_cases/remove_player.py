from app.domain.repositories.game_repository import GameRepository


class RemovePlayerUseCase:

    def __init__(
        self,
        game_repository: GameRepository,
    ):
        self.game_repository = game_repository

    async def execute(
        self,
        game_id: str,
        player_id: str,
    ):
        game = await self.game_repository.get(game_id)

        if not game:
            raise ValueError(
                f"Game with ID {game_id} not found."
            )

        game.players = [
            player
            for player in game.players
            if player.user_id != player_id
        ]

        await self.game_repository.update(game)

        return game