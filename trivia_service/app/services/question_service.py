from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError

from app.dtos.question import QuestionCreateDTO, QuestionResponseDTO, QuestionUpdateDTO
from app.core.exceptions import TriviaErrorMessages, TriviaException
from app.models.question import Question


class QuestionService:
    def __init__(self, question_repository):
        self.question_repository = question_repository

    def get_questions(
        self,
        package_id: int,
        player_id: UUID | None = None,
    ) -> list[QuestionResponseDTO]:
        questions = self.question_repository.get_questions(package_id, player_id)
        return [self._from_entity_to_dto(question) for question in questions]

    def get_question(
        self,
        question_id: int,
        player_id: UUID | None = None,
    ) -> QuestionResponseDTO:
        question = self.question_repository.get_question_by_id(question_id, player_id)

        if not question:
            raise TriviaException(TriviaErrorMessages.QUESTION_NOT_FOUND)

        return self._from_entity_to_dto(question)

    def create_question(self, question: QuestionCreateDTO, player_id: UUID) -> QuestionResponseDTO:
        statement = question.statement.strip()
        if not statement:
            raise TriviaException(TriviaErrorMessages.INVALID_REQUEST)

        package = self.question_repository.get_package_by_id(question.package_id)
        if not package:
            raise TriviaException(TriviaErrorMessages.PACKAGE_NOT_FOUND)
        if package.author_id != player_id:
            raise TriviaException(TriviaErrorMessages.UNAUTHORIZED_QUESTION_UPDATE)

        duplicate = self.question_repository.get_duplicate(question.package_id, statement)
        if duplicate:
            if duplicate.explanation == question.explanation:
                return self._from_entity_to_dto(duplicate)
            raise TriviaException(TriviaErrorMessages.DUPLICATE_RESOURCE_CONFLICT)
        
        question.statement = statement
        question_entity = self._from_dto_to_entity(question)
        
        try:
            question_entity = self.question_repository.create_question(question_entity)
            self.question_repository.session.commit()
        except IntegrityError:
            self.question_repository.session.rollback()
            duplicate = self.question_repository.get_duplicate(question.package_id, statement)
            if duplicate and duplicate.explanation == question.explanation:
                return self._from_entity_to_dto(duplicate)
            if duplicate:
                raise TriviaException(TriviaErrorMessages.DUPLICATE_RESOURCE_CONFLICT)
            raise

        return self._from_entity_to_dto(question_entity)

    def update_question(
        self,
        question_id: int,
        question: QuestionUpdateDTO,
        player_id: UUID,
    ) -> QuestionResponseDTO:
        existing_question = self.question_repository.get_question_by_id(question_id, player_id)

        if not existing_question:
            raise TriviaException(TriviaErrorMessages.QUESTION_NOT_FOUND)

        if existing_question.package.author_id != player_id:
            raise TriviaException(TriviaErrorMessages.UNAUTHORIZED_QUESTION_UPDATE)

        question_data = question.model_dump(exclude_unset=True)
        if "statement" in question_data and question_data["statement"] is None:
            question_data.pop("statement")

        if "statement" in question_data:
            question_data["statement"] = question_data["statement"].strip()
            
            if not question_data["statement"]:
                question_data.pop("statement")
            
        if any(getattr(existing_question, key) == value for key, value in question_data.items()):
            return self._from_entity_to_dto(existing_question)
        
        if "statement" in question_data:
            duplicate = self.question_repository.get_duplicate(
                existing_question.package_id,
                question_data["statement"],
            )
            
            if duplicate and duplicate.id != existing_question.id:
                raise TriviaException(TriviaErrorMessages.DUPLICATE_RESOURCE_CONFLICT)
            
        for key, value in question_data.items():
            setattr(existing_question, key, value)
            
        existing_question.updated_at = datetime.now(timezone.utc)

        try:
            question_entity = self.question_repository.update_question(existing_question)
            self.question_repository.session.commit()
        except IntegrityError as exc:
            self.question_repository.session.rollback()
            raise TriviaException(TriviaErrorMessages.DUPLICATE_RESOURCE_CONFLICT) from exc

        return self._from_entity_to_dto(question_entity)

    def delete_question(self, question_id: int, player_id: UUID) -> None:
        existing_question = self.question_repository.get_question_by_id(question_id, player_id)

        if not existing_question:
            return

        if existing_question.package.author_id != player_id:
            raise TriviaException(TriviaErrorMessages.UNAUTHORIZED_QUESTION_UPDATE)

        self.question_repository.delete_question(existing_question)
        self.question_repository.session.commit()

    @staticmethod
    def _from_entity_to_dto(question: Question) -> QuestionResponseDTO:
        return QuestionResponseDTO(
            id=question.id,
            package_id=question.package_id,
            statement=question.statement,
            explanation=question.explanation,
            created_at=question.created_at,
            updated_at=question.updated_at
        )

    @staticmethod
    def _from_dto_to_entity(question_dto: QuestionCreateDTO) -> Question:
        return Question(
            package_id=question_dto.package_id,
            statement=question_dto.statement,
            explanation=question_dto.explanation
        )