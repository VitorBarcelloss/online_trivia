import asyncio

from app.presentation.game_dependencies import (
    connection_manager,
    game_repository,
    next_question_use_case,
    resolve_question_use_case,
)


question_timers: dict[str, asyncio.Task] = {}

question_locks: dict[str, asyncio.Lock] = {}


def build_public_question(question) -> dict:
    return {
        "id": question.id,
        "order": question.order,
        "statement": question.statement,
        "options": question.options,
    }


def build_ranking(game) -> list[dict]:
    return [
        {
            "user_id": player.user_id,
            "nickname": player.nickname,
            "score": player.score,
        }
        for player in sorted(
            game.players,
            key=lambda player: player.score,
            reverse=True,
        )
    ]


def get_question_lock(
    game_id: str,
) -> asyncio.Lock:
    if game_id not in question_locks:
        question_locks[game_id] = asyncio.Lock()

    return question_locks[game_id]


def cancel_question_timer(
    game_id: str,
) -> None:
    task = question_timers.pop(
        game_id,
        None,
    )

    if task and not task.done():
        task.cancel()


def cleanup_game(
    game_id: str,
) -> None:
    cancel_question_timer(game_id)

    question_locks.pop(
        game_id,
        None,
    )


def start_question_timer(
    game_id: str,
    question_time: int,
) -> None:
    cancel_question_timer(game_id)

    question_timers[game_id] = asyncio.create_task(
        question_timer(
            game_id=game_id,
            question_time=question_time,
        )
    )


async def question_timer(
    game_id: str,
    question_time: int,
) -> None:
    try:
        await asyncio.sleep(question_time)

        await resolve_and_next_question(
            game_id=game_id,
        )

    except asyncio.CancelledError:
        pass


async def resolve_and_next_question(
    game_id: str,
) -> None:
    lock = get_question_lock(game_id)

    should_cleanup = False

    async with lock:
        game = await game_repository.get(game_id)

        if not game:
            return

        if game.status != "IN_PROGRESS":
            return

        if not game.current_question:
            return

        question = game.current_question
        question_id = question.id

        game = await resolve_question_use_case.execute(
            game_id=game_id,
        )

        await connection_manager.broadcast(
            game_id=game_id,
            message={
                "type": "question_resolved",
                "question_id": question_id,
                "correct_answer": question.correct_answer,
                "explanation": question.explanation,
            },
        )

        await connection_manager.broadcast(
            game_id=game_id,
            message={
                "type": "ranking_updated",
                "ranking": build_ranking(game),
            },
        )

        game = await next_question_use_case.execute(
            game_id=game_id,
        )

        if game.status == "FINISHED":
            await connection_manager.broadcast(
                game_id=game_id,
                message={
                    "type": "game_finished",
                    "ranking": build_ranking(game),
                },
            )

            should_cleanup = True

        else:
            await connection_manager.broadcast(
                game_id=game_id,
                message={
                    "type": "next_question",
                    "question": build_public_question(
                        game.current_question,
                    ),
                },
            )

            start_question_timer(
                game_id=game_id,
                question_time=game.question_time,
            )

    if should_cleanup:
        cleanup_game(game_id)