from pydantic import BaseModel


class GamePlayer(BaseModel):
    user_id: str
    nickname: str
    score: int