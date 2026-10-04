
from typing import Optional

from pydantic import BaseModel, Field

from app.domain.entities.game_player import GamePlayer
from app.domain.entities.game_question import GameQuestion
from app.domain.entities.player_answer import PlayerAnswer

class Game(BaseModel):
    id: str
    room_id: str
    host_id: str
    status: str
    current_question: GameQuestion | None = None
    questions: list[GameQuestion]
    players: list[GamePlayer]
    answers: list[PlayerAnswer] = Field(default_factory=list)
    question_time: int
    show_ranking: bool