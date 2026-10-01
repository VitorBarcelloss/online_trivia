from uuid import UUID
from datetime import date

from app.dtos.question import QuestionDTO
from app.core.exceptions import TriviaErrorMessages, TriviaException
from app.models.question import Question


class QuestionService:
    def __init__(self, question_repository):
        self.question_repository = question_repository

    def get_questions(
        self,
        package_id: int,
        player_id: UUID | None = None,
    ) -> list[QuestionDTO]:
        questions = self.question_repository.get_questions(package_id, player_id)

        if not questions:
            raise TriviaException(TriviaErrorMessages.QUESTIONS_NOT_FOUND)

        return [self._from_entity_to_dto(question) for question in questions]

    def get_question(
        self,
        question_id: int,
        player_id: UUID | None = None,
    ) -> QuestionDTO:
        question = self.question_repository.get_question_by_id(question_id, player_id)

        if not question:
            raise TriviaException(TriviaErrorMessages.QUESTION_NOT_FOUND)

        return self._from_entity_to_dto(question)

    def create_question(self, question: QuestionDTO, player_id: UUID) -> QuestionDTO:
        if not question.package_id:
            raise TriviaException(TriviaErrorMessages.PACKAGE_ID_MISSING)

        package = self.question_repository.get_package_by_id(question.package_id)
        if not package:
            raise TriviaException(TriviaErrorMessages.PACKAGE_NOT_FOUND)
        if package.author_id != player_id:
            raise TriviaException(TriviaErrorMessages.UNAUTHORIZED_QUESTION_UPDATE)

        question_entity = self._from_dto_to_entity(question)
        question_entity.created_at = date.today()
        question_entity = self.question_repository.create_question(question_entity)

        if not question_entity.id:
            raise TriviaException(TriviaErrorMessages.QUESTION_CREATION_FAILED)

        return self._from_entity_to_dto(question_entity)

    def update_question(
        self,
        question_id: int,
        question: QuestionDTO,
        player_id: UUID,
    ) -> QuestionDTO:
        existing_question = self.question_repository.get_question_by_id(question_id, player_id)

        if not existing_question:
            raise TriviaException(TriviaErrorMessages.QUESTION_NOT_FOUND)

        if existing_question.package.author_id != player_id:
            raise TriviaException(TriviaErrorMessages.UNAUTHORIZED_QUESTION_UPDATE)

        question_data = question.model_dump(exclude_unset=True)
        for key, value in question_data.items():
            setattr(existing_question, key, value)

        question_entity = self.question_repository.update_question(existing_question)

        return self._from_entity_to_dto(question_entity)

    def delete_question(self, question_id: int, player_id: UUID) -> None:
        existing_question = self.question_repository.get_question_by_id(question_id, player_id)

        if not existing_question:
            raise TriviaException(TriviaErrorMessages.QUESTION_NOT_FOUND)

        if existing_question.package.author_id != player_id:
            raise TriviaException(TriviaErrorMessages.UNAUTHORIZED_QUESTION_UPDATE)

        self.question_repository.delete_question(existing_question)

    @staticmethod
    def _from_entity_to_dto(question: Question) -> QuestionDTO:
        return QuestionDTO(
            id=question.id,
            package_id=question.package_id,
            statement=question.statement,
            explanation=question.explanation,
            created_at=question.created_at,
            updated_at=question.updated_at
        )

    @staticmethod
    def _from_dto_to_entity(question_dto: QuestionDTO) -> Question:
        return Question(
            package_id=question_dto.package_id,
            statement=question_dto.statement,
            explanation=question_dto.explanation
        )