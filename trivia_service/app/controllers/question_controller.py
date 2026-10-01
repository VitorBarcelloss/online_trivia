from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from app.database.database import get_db
from app.dtos.question import QuestionCreateDTO, QuestionResponseDTO, QuestionUpdateDTO
from app.repositories.question_repository import QuestionRepository
from app.services.question_service import QuestionService

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.get("", response_model=list[QuestionResponseDTO])
def get_all_questions(
	package_id: int,
	player_id: UUID | None = None,
	db = Depends(get_db)
) -> list[QuestionResponseDTO]:
	question_repository = QuestionRepository(db)
	question_service = QuestionService(question_repository)
	return question_service.get_questions(package_id, player_id)



@router.get("/{question_id}", response_model=QuestionResponseDTO)
def get_question(
    question_id: int,
    player_id: UUID | None = None,
    db = Depends(get_db)
) -> QuestionResponseDTO:
	question_repository = QuestionRepository(db)
	question_service = QuestionService(question_repository)
	return question_service.get_question(question_id, player_id)


@router.post("", response_model=QuestionResponseDTO, status_code=status.HTTP_201_CREATED)
def create_question(
	question: QuestionCreateDTO,
    player_id: UUID,
    db = Depends(get_db)
) -> QuestionResponseDTO:
	question_repository = QuestionRepository(db)
	question_service = QuestionService(question_repository)
	return question_service.create_question(question, player_id)

@router.patch("/{question_id}", response_model=QuestionResponseDTO)
def update_question(
	question_id: int,
	question: QuestionUpdateDTO,
	player_id: UUID,
	db = Depends(get_db)
) -> QuestionResponseDTO:
	question_repository = QuestionRepository(db)
	question_service = QuestionService(question_repository)
	return question_service.update_question(question_id, question, player_id)


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    question_id: int,
    player_id: UUID,
    db = Depends(get_db)
) -> Response:
	question_repository = QuestionRepository(db)
	question_service = QuestionService(question_repository)
	question_service.delete_question(question_id, player_id)
	return Response(status_code=status.HTTP_204_NO_CONTENT)