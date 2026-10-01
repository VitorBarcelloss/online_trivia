from pydantic import BaseModel


class AlternativeDTO(BaseModel):
    id: int | None = None
    question_id: int
    text: str
    is_correct: bool