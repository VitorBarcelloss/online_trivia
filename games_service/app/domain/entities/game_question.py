from pydantic import BaseModel


class GameQuestion(BaseModel):
    id: str
    order: int
    statement: str
    options: list[str]
    correct_answer: str
    explanation: str