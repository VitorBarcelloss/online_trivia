from pydantic import BaseModel, Field


class AlternativeCreateDTO(BaseModel):
    question_id: int
    text: str = Field(min_length=1, max_length=500)
    is_correct: bool


class AlternativeUpdateDTO(BaseModel):
    text: str | None = Field(default=None, min_length=1, max_length=500)
    is_correct: bool | None = None


class AlternativeResponseDTO(BaseModel):
    id: int
    question_id: int
    text: str
    is_correct: bool