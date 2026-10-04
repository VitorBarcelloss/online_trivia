from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.dtos.question_package import (
    GameQuestionResponseDTO,
    QuestionPackageCreateDTO,
    QuestionPackageResponseDTO,
    QuestionPackageUpdateDTO,
)
from app.repositories.question_package_repository import QuestionPackageRepository
from app.models.question_package import QuestionPackage
from app.core.exceptions import TriviaErrorMessages, TriviaException

class QuestionPackageService:
    def __init__(self, package_repository: QuestionPackageRepository):
        self.package_repository = package_repository

    def get_question_packages(
        self,
        player_id: UUID | None = None,
    ) -> list[QuestionPackageResponseDTO]:
        packages = self.package_repository.get_packages(player_id)
        return [self._from_entity_to_dto(package) for package in packages ]

    def get_question_package__by_id_service(
        self,
        package_id: int,
        player_id: UUID | None = None
    ) -> QuestionPackageResponseDTO:
        package = self.package_repository.get_package_by_id(package_id)

        if not package:
            raise TriviaException(TriviaErrorMessages.PACKAGE_NOT_FOUND)

        if not package.is_public and player_id != package.author_id:
            raise TriviaException(TriviaErrorMessages.UNAUTHORIZED_PACKAGE_UPDATE)

        return self._from_entity_to_dto(package)
    
    def get_game_questions(
        self,
        package_id: int,
        player_id: UUID | None = None
    ) -> list[GameQuestionResponseDTO]:
        package = self.package_repository.get_package_by_id(package_id)

        if not package:
            raise TriviaException(TriviaErrorMessages.PACKAGE_NOT_FOUND)

        if not package.is_public and player_id != package.author_id:
            raise TriviaException(TriviaErrorMessages.UNAUTHORIZED_PACKAGE_UPDATE)

        questions = package.questions
        
        return [
            GameQuestionResponseDTO(
                package_id=question.package_id,
                question_id=question.id,
                statement=question.statement,
                alternatives=[
                    {
                        "id": alternative.id,
                        "text": alternative.text
                    }
                    for alternative in question.alternatives
                ],
                correct_answer=question.correct_answer,
                explanation=question.explanation
            )
            for question in questions
        ]

    def create_question_package(
        self,
        package_dto: QuestionPackageCreateDTO,
        player_id: UUID,
    ) -> QuestionPackageResponseDTO:
        data = package_dto.model_dump()
        data["name"] = data["name"].strip()
        
        if not data["name"]:
            raise TriviaException(TriviaErrorMessages.INVALID_REQUEST)
        
        data["name_key"] = data["name"].casefold()
        
        existing = self.package_repository.get_by_author_and_name(player_id, data["name_key"])
        if existing:
            return self._existing_or_conflict(existing, data)

        package = QuestionPackage(author_id=player_id, created_at=datetime.now(timezone.utc), **data)
        try:
            self.package_repository.create_question_package(package)
            self.package_repository.session.commit()
        except IntegrityError:
            self.package_repository.session.rollback()
            existing = self.package_repository.get_by_author_and_name(player_id, data["name_key"])
            if existing:
                return self._existing_or_conflict(existing, data)
            raise
        return self._from_entity_to_dto(package)


    def update_question_package(
        self,
        package_id: int,
        package: QuestionPackageUpdateDTO,
        player_id: UUID,
    ) -> QuestionPackageResponseDTO:
        existing_package = self.package_repository.get_package_by_id(package_id)

        if not existing_package:
            raise TriviaException(TriviaErrorMessages.PACKAGE_NOT_FOUND)

        if existing_package.author_id != player_id:
            raise TriviaException(TriviaErrorMessages.UNAUTHORIZED_PACKAGE_UPDATE)

        update_data = package.model_dump(exclude_unset=True)
        
        if "is_public" in update_data and update_data["is_public"] is None:
            update_data.pop("is_public")
        
        if "name" in update_data and update_data["name"] is not None:
            update_data["name"] = update_data["name"].strip()
            if not update_data["name"]:
                update_data.pop("name")
            
            update_data["name_key"] = update_data["name"].casefold()
            
        elif "name" in update_data and update_data["name"] is None:
            update_data.pop("name")
        
        if any(getattr(existing_package, key) == value for key, value in update_data.items()):
            return self._from_entity_to_dto(existing_package)
        
        if "name_key" in update_data:
            duplicate = self.package_repository.get_by_author_and_name(
                player_id,
            update_data["name_key"],
            )
            if duplicate and duplicate.id != existing_package.id:
                raise TriviaException(TriviaErrorMessages.DUPLICATE_RESOURCE_CONFLICT)
            
        for key, value in update_data.items():
            setattr(existing_package, key, value)
            
        existing_package.updated_at = datetime.now(timezone.utc)

        try:
            updated_package = self.package_repository.update_question_package(existing_package)
            self.package_repository.session.commit()
        except IntegrityError as exc:
            self.package_repository.session.rollback()
            raise TriviaException(TriviaErrorMessages.DUPLICATE_RESOURCE_CONFLICT) from exc

        return self._from_entity_to_dto(updated_package)

    def delete_question_package(
        self,
        package_id: int,
        player_id: UUID
        ) -> None:
        existing_package = self.package_repository.get_package_by_id(package_id)

        if not existing_package:
            return

        if existing_package.author_id != player_id:
            raise TriviaException(TriviaErrorMessages.UNAUTHORIZED_PACKAGE_UPDATE)

        self.package_repository.delete_question_package(existing_package)
        self.package_repository.session.commit()

    @staticmethod
    def _from_entity_to_dto(package: QuestionPackage) -> QuestionPackageResponseDTO:
        return QuestionPackageResponseDTO(
            id=package.id,
            name=package.name,
            description=package.description,
            author_id=package.author_id,
            package_type=package.package_type,
            is_public=package.is_public,
            created_at=package.created_at,
            updated_at=package.updated_at,
        )

    def _existing_or_conflict(
        self,
        existing: QuestionPackage,
        data: dict,
    ) -> QuestionPackageResponseDTO:
        fields = ("name", "description", "package_type", "is_public")
        
        if all(getattr(existing, field) == data[field] for field in fields):
            return self._from_entity_to_dto(existing)
        
        raise TriviaException(TriviaErrorMessages.DUPLICATE_RESOURCE_CONFLICT)
