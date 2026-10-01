from datetime import date

from pydantic import BaseModel


class QuestionDTO(BaseModel):
    id: int | None = None
    package_id: int
    statement: str
    explanation: str | None = None
    created_at: date | None = None
    updated_at: date | None = None