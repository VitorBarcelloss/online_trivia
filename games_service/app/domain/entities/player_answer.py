from datetime import datetime
from pydantic import BaseModel


class PlayerAnswer(BaseModel):
    player_id: str
    question_id: str
    answer: str
    answered_at: datetime
    correct: bool