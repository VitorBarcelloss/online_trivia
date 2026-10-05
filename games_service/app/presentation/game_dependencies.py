from config.settings import settings

from app.application.use_cases.add_player import AddPlayerUseCase
from app.application.use_cases.finish_game import FinishGameUseCase
from app.application.use_cases.next_question import NextQuestionUseCase
from app.application.use_cases.remove_player import RemovePlayerUseCase
from app.application.use_cases.resolve_question import ResolveQuestionUseCase
from app.application.use_cases.start_game import StartGameUseCase
from app.application.use_cases.submit_answer import SubmitAnswerUseCase

from app.infrastructure.clients.room_client import RoomClient
from app.infrastructure.clients.trivia_client import TriviaClient
from app.infrastructure.repositories.redis_game_repository import (
    RedisGameRepository,
)

from app.presentation.websocket.connection_manager import (
    ConnectionManager,
)


connection_manager = ConnectionManager()

game_repository = RedisGameRepository()


room_client = RoomClient(
    base_url=settings.room_service_url,
)

trivia_client = TriviaClient(
    base_url=settings.trivia_service_url,
)


start_game_use_case = StartGameUseCase(
    game_repository=game_repository,
    room_client=room_client,
    trivia_client=trivia_client,
)

submit_answer_use_case = SubmitAnswerUseCase(
    game_repository=game_repository,
)

resolve_question_use_case = ResolveQuestionUseCase(
    game_repository=game_repository,
)

next_question_use_case = NextQuestionUseCase(
    game_repository=game_repository,
)

finish_game_use_case = FinishGameUseCase(
    game_repository=game_repository,
)

add_player_use_case = AddPlayerUseCase(
    game_repository=game_repository,
)

remove_player_use_case = RemovePlayerUseCase(
    game_repository=game_repository,
)
