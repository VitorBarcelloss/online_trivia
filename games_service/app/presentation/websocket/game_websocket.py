from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)

from app.presentation.game_dependencies import (
    connection_manager,
    finish_game_use_case,
    game_repository,
    submit_answer_use_case,
)

from app.presentation.game_runtime import (
    build_public_question,
    build_ranking,
    cancel_question_timer,
    cleanup_game,
    resolve_and_next_question,
)

from app.presentation.websocket.events import (
    FinishGameEvent,
    SubmitAnswerEvent,
)


router = APIRouter()


@router.websocket("/{room_code}")
async def game_websocket(
    websocket: WebSocket,
    room_code: str,
    player_id: str,
):
    game_id: str | None = None

    try:
        game_id = await connection_manager.connect(
            room_code=room_code,
            player_id=player_id,
            websocket=websocket,
        )

        if game_id:
            game = await game_repository.get(
                game_id,
            )

            if game and game.current_question:
                await connection_manager.send_to_player(
                    game_id=game_id,
                    player_id=player_id,
                    message={
                        "type": "question_started",
                        "question": build_public_question(
                            game.current_question,
                        ),
                    },
                )

        while True:
            data = await websocket.receive_json()

            event_type = data.get("type")

            if event_type == "submit_answer":
                game_id = connection_manager.get_game_id(
                    room_code,
                )

                if not game_id:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": "Game has not started.",
                        }
                    )
                    continue

                try:
                    event = SubmitAnswerEvent.model_validate(
                        data,
                    )

                    await submit_answer_use_case.execute(
                        game_id=game_id,
                        player_id=player_id,
                        answer=event.answer,
                    )

                    await connection_manager.send_to_player(
                        game_id=game_id,
                        player_id=player_id,
                        message={
                            "type": "answer_submitted",
                        },
                    )

                    game = await game_repository.get(
                        game_id,
                    )

                    if not game:
                        continue

                    if not game.current_question:
                        continue

                    question_id = game.current_question.id

                    answers = [
                        answer
                        for answer in game.answers
                        if answer.question_id == question_id
                    ]

                    active_players = [
                        player
                        for player in game.players
                    ]

                    if (
                        active_players
                        and len(answers) >= len(active_players)
                    ):
                        cancel_question_timer(
                            game_id,
                        )

                        await resolve_and_next_question(
                            game_id=game_id,
                            expected_question_id=question_id,
                        )

                except ValueError as error:
                    await connection_manager.send_to_player(
                        game_id=game_id,
                        player_id=player_id,
                        message={
                            "type": "error",
                            "message": str(error),
                        },
                    )

            elif event_type == "finish_game":
                game_id = connection_manager.get_game_id(
                    room_code,
                )

                if not game_id:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": "Game has not started.",
                        }
                    )
                    continue

                try:
                    FinishGameEvent.model_validate(
                        data,
                    )

                    game = await finish_game_use_case.execute(
                        game_id=game_id,
                        player_id=player_id,
                    )

                    await connection_manager.broadcast(
                        game_id=game_id,
                        message={
                            "type": "game_finished",
                            "ranking": build_ranking(game),
                        },
                    )

                    cleanup_game(
                        game_id=game_id,
                    )

                    connection_manager.cleanup_game(
                        room_code=room_code,
                        game_id=game_id,
                    )

                except ValueError as error:
                    await connection_manager.send_to_player(
                        game_id=game_id,
                        player_id=player_id,
                        message={
                            "type": "error",
                            "message": str(error),
                        },
                    )

            else:
                game_id = connection_manager.get_game_id(
                    room_code,
                )

                if game_id:
                    await connection_manager.send_to_player(
                        game_id=game_id,
                        player_id=player_id,
                        message={
                            "type": "error",
                            "message": "Unknown event.",
                        },
                    )

    except WebSocketDisconnect:
        connection_manager.disconnect(
            room_code=room_code,
            player_id=player_id,
        )
