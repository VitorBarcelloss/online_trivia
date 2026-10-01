from datetime import datetime

from pydantic import BaseModel, Field


class QuestionCreateDTO(BaseModel):
    package_id: int = Field(gt=0)
    statement: str = Field(min_length=1)
    explanation: str | None = None


class QuestionUpdateDTO(BaseModel):
    statement: str | None = Field(default=None, min_length=1)
    explanation: str | None = None


class QuestionResponseDTO(BaseModel):
    id: int
    package_id: int
    statement: str
    explanation: str | None = None
    created_at: datetime
    updated_at: datetime