from uuid import UUID

from fastapi import APIRouter, Depends
from app.database.database import get_db
from app.dtos.question import QuestionDTO
from app.repositories.question_repository import QuestionRepository
from app.services.question_service import QuestionService

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.get("", response_model=list[QuestionDTO])
def get_all_questions(
	package_id: int,
	player_id: UUID | None = None,
	db = Depends(get_db)
) -> list[QuestionDTO]:
	question_repository = QuestionRepository(db)
	question_service = QuestionService(question_repository)
	return question_service.get_questions(package_id, player_id)



@router.get("/{question_id}", response_model=QuestionDTO)
def get_question(
    question_id: int,
    player_id: UUID | None = None,
    db = Depends(get_db)
) -> QuestionDTO:
	question_repository = QuestionRepository(db)
	question_service = QuestionService(question_repository)
	return question_service.get_question(question_id, player_id)


@router.post("", response_model=QuestionDTO)
def create_question(
    question: QuestionDTO,
    player_id: UUID,
    db = Depends(get_db)
) -> QuestionDTO:
	question_repository = QuestionRepository(db)
	question_service = QuestionService(question_repository)
	return question_service.create_question(question, player_id)

@router.put("/{question_id}", response_model=QuestionDTO)
def update_question(
	question_id: int,
	question: QuestionDTO,
	player_id: UUID,
	db = Depends(get_db)
) -> QuestionDTO:
	question_repository = QuestionRepository(db)
	question_service = QuestionService(question_repository)
	return question_service.update_question(question_id, question, player_id)


@router.delete("/{question_id}")
def delete_question(
    question_id: int,
    player_id: UUID,
    db = Depends(get_db)
) -> None:
	question_repository = QuestionRepository(db)
	question_service = QuestionService(question_repository)
	question_service.delete_question(question_id, player_id)