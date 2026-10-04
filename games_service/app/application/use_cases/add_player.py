from app.domain.entities.game_player import GamePlayer
from app.domain.repositories.game_repository import GameRepository


class AddPlayerUseCase:

    def __init__(
        self,
        game_repository: GameRepository,
    ):
        self.game_repository = game_repository

    async def execute(
        self,
        game_id: str,
        player_id: str,
        nickname: str,
    ):
        game = await self.game_repository.get(game_id)

        if not game:
            raise ValueError(
                f"Game with ID {game_id} not found."
            )

        if game.status != "IN_PROGRESS":
            return game

        already_in_game = any(
            player.user_id == player_id
            for player in game.players
        )

        if already_in_game:
            return game

        game.players.append(
            GamePlayer(
                user_id=player_id,
                nickname=nickname,
                score=0,
            )
        )

        await self.game_repository.update(game)

        return game