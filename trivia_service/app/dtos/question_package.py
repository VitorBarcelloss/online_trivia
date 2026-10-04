from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class QuestionPackageCreateDTO(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    description: str | None = None
    package_type: str | None = None
    is_public: bool = False


class QuestionPackageUpdateDTO(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = None
    package_type: str | None = None
    is_public: bool | None = None


class QuestionPackageResponseDTO(BaseModel):
    id: int
    name: str
    description: str | None = None
    author_id: UUID
    package_type: str | None = None
    is_public: bool = False
    created_at: datetime
    updated_at: datetime
    
class GameQuestionResponseDTO(BaseModel):
    package_id: UUID
    question_id: UUID
    statement: str
    alternatives: list[dict]
    correct_answer: str
    explanation: str | None = None