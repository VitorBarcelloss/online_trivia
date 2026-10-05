from fastapi import APIRouter, HTTPException

from app.presentation.game_dependencies import (
    connection_manager,
    game_repository,
    start_game_use_case,
)

from app.presentation.game_runtime import (
    build_public_question,
    build_ranking,
    start_question_timer,
)


router = APIRouter()


@router.post("/start")
async def start_game(
    room_code: str,
    player_id: str,
):
    try:
        game = await start_game_use_case.execute(
            room_code=room_code,
            player_id=player_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    connection_manager.bind_room_to_game(
        room_code=room_code,
        game_id=game.id,
    )

    await connection_manager.broadcast(
        game_id=game.id,
        message={
            "type": "game_started",
            "game_id": game.id,
        },
    )

    await connection_manager.broadcast(
        game_id=game.id,
        message={
            "type": "question_started",
            "question": build_public_question(
                game.current_question,
            ),
        },
    )

    start_question_timer(
        game_id=game.id,
        question_time=game.question_time,
    )

    return game


@router.get("/{game_id}")
async def get_game(
    game_id: str,
):
    game = await game_repository.get(
        game_id,
    )

    if not game:
        raise HTTPException(
            status_code=404,
            detail="Game not found.",
        )

    return {
        "id": game.id,
        "room_id": game.room_id,
        "host_id": game.host_id,
        "status": game.status,
        "question": (
            build_public_question(
                game.current_question,
            )
            if game.current_question
            else None
        ),
        "ranking": build_ranking(game),
        "question_time": game.question_time,
        "show_ranking": game.show_ranking,
    }


@router.get("/{game_id}/review")
async def get_game_review(
    game_id: str,
):
    game = await game_repository.get(
        game_id,
    )

    if not game:
        raise HTTPException(
            status_code=404,
            detail="Game not found.",
        )

    review = []

    for question in game.questions:
        question_answers = [
            answer
            for answer in game.answers
            if answer.question_id == question.id
        ]

        answers = []

        for answer in question_answers:
            player = next(
                (
                    player
                    for player in game.players
                    if player.user_id == answer.player_id
                ),
                None,
            )

            answers.append(
                {
                    "player_id": answer.player_id,
                    "nickname": (
                        player.nickname
                        if player
                        else answer.player_id
                    ),
                    "answer": answer.answer,
                    "correct": answer.correct,
                    "answered_at": answer.answered_at,
                }
            )

        review.append(
            {
                "question_id": question.id,
                "order": question.order,
                "statement": question.statement,
                "options": question.options,
                "correct_answer": question.correct_answer,
                "explanation": question.explanation,
                "answers": answers,
            }
        )

    return {
        "game_id": game.id,
        "status": game.status,
        "ranking": build_ranking(game),
        "questions": review,
    }