from datetime import date
from uuid import UUID

from app.dtos.question_package import QuestionPackageDTO
from app.repositories.question_package_repository import QuestionPackageRepository
from app.models.question_package import QuestionPackage
from app.core.exceptions import TriviaErrorMessages, TriviaException

class QuestionPackageService:
    def __init__(self, package_repository: QuestionPackageRepository):
        self.package_repository = package_repository

    def get_question_packages(
        self,
        player_id: UUID | None = None,
    ) -> list[QuestionPackageDTO]:
        packages = self.package_repository.get_packages(player_id)

        if not packages:
            raise TriviaException(TriviaErrorMessages.PACKAGE_NOT_FOUND)

        return [self._from_entity_to_dto(package) for package in packages ]

    def get_question_package__by_id_service(
        self,
        package_id: int,
        player_id: UUID | None = None
    ) -> QuestionPackageDTO:
        package = self.package_repository.get_package_by_id(package_id)

        if not package:
            raise TriviaException(TriviaErrorMessages.PACKAGE_NOT_FOUND)

        if not package.is_public and player_id != package.author_id:
            raise TriviaException(TriviaErrorMessages.UNAUTHORIZED_PACKAGE_UPDATE)

        return self._from_entity_to_dto(package)

    def create_question_package(
        self,
        package_dto: QuestionPackageDTO,
        player_id: UUID,
    ) -> QuestionPackageDTO:
        package = self._from_dto_to_entity(package_dto, player_id)
        package = self.package_repository.create_question_package(package)

        if not package.id:
            raise TriviaException(TriviaErrorMessages.PACKAGE_CREATION_FAILED)

        return self._from_entity_to_dto(package)


    def update_question_package(
        self,
        package_id: int,
        package: QuestionPackageDTO,
        player_id: UUID,
    ) -> QuestionPackageDTO:
        existing_package = self.package_repository.get_package_by_id(package_id)

        if not existing_package:
            raise TriviaException(TriviaErrorMessages.PACKAGE_NOT_FOUND)

        if existing_package.author_id != player_id:
            raise TriviaException(TriviaErrorMessages.UNAUTHORIZED_PACKAGE_UPDATE)

        update_data = package.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing_package, key, value)

        updated_package = self.package_repository.update_question_package(existing_package)

        return self._from_entity_to_dto(updated_package)

    def delete_question_package(
        self,
        package_id: int,
        player_id: UUID
        ) -> None:
        existing_package = self.package_repository.get_package_by_id(package_id)

        if not existing_package:
            raise TriviaException(TriviaErrorMessages.PACKAGE_NOT_FOUND)

        if existing_package.author_id != player_id:
            raise TriviaException(TriviaErrorMessages.UNAUTHORIZED_PACKAGE_UPDATE)

        self.package_repository.delete_question_package(existing_package)

    @staticmethod
    def _from_entity_to_dto(package: QuestionPackage) -> QuestionPackageDTO:
        return QuestionPackageDTO(
            id=package.id,
            name=package.name,
            description=package.description,
            author_id=package.author_id,
            package_type=package.package_type,
            is_public=package.is_public,
            created_at=package.created_at,
            updated_at=package.updated_at,
        )

    @staticmethod
    def _from_dto_to_entity(
        package_dto: QuestionPackageDTO,
        player_id: UUID,
    ) -> QuestionPackage:
        return QuestionPackage(
            name=package_dto.name,
            description=package_dto.description,
            author_id=player_id,
            package_type=package_dto.package_type,
            is_public=package_dto.is_public,
            created_at=date.today(),
        )
