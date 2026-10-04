from games_service.app.domain.repositories.game_repository import GameRepository


class ResolveQuestionUseCase:

    def __init__(
        self,
        game_repository: GameRepository
    ):
        self.game_repository = game_repository

    async def execute(
        self,
        game_id: str
    ):

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

        current_question_id = game.current_question.id

        answers = [
            answer
            for answer in game.answers
            if answer.question_id == current_question_id
        ]

        correct_answers = sorted(
            [
                answer
                for answer in answers
                if answer.correct
            ],
            key=lambda answer: answer.answered_at
        )

        multipliers = {
            0: 5,
            1: 3,
            2: 2,
        }

        for position, answer in enumerate(correct_answers):

            player = next(
                (
                    player
                    for player in game.players
                    if player.user_id == answer.player_id
                ),
                None
            )

            if not player:
                continue

            multiplier = multipliers.get(position, 1)

            player.score += 100 * multiplier

        await self.game_repository.update(game)

        return game