from datetime import date
from uuid import UUID

from pydantic import BaseModel


class QuestionPackageDTO(BaseModel):
    id: int | None = None
    name: str | None = None
    description: str | None = None
    author_id: UUID | None = None
    package_type: str | None = None
    is_public: bool = False
    created_at: date | None = None
    updated_at: date | None = None