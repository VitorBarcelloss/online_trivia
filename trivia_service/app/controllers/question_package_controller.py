from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from app.database.database import get_db

from app.dtos.question_package import (
	QuestionPackageCreateDTO,
	QuestionPackageResponseDTO,
	QuestionPackageUpdateDTO,
)
from app.repositories.question_package_repository import QuestionPackageRepository
from app.services.question_package_service import QuestionPackageService

router = APIRouter(prefix="/question-packages", tags=["Question Packages"])


@router.get("", response_model=list[QuestionPackageResponseDTO])
def get_question_packages(
    player_id: UUID | None = None,
    db = Depends(get_db)
	) -> list[QuestionPackageResponseDTO]:
	package_repository = QuestionPackageRepository(db)
	package_service = QuestionPackageService(package_repository)
	return package_service.get_question_packages(player_id)



@router.get("/{package_id}", response_model=QuestionPackageResponseDTO)
def get_question_package__by_id(
	package_id: int,
	player_id: UUID | None = None,
	db = Depends(get_db)
) -> QuestionPackageResponseDTO:
	package_repository = QuestionPackageRepository(db)
	package_service = QuestionPackageService(package_repository)
	return package_service.get_question_package__by_id_service(package_id, player_id)


@router.post("", response_model=QuestionPackageResponseDTO, status_code=status.HTTP_201_CREATED)
def create_question_package(
	package: QuestionPackageCreateDTO,
    player_id: UUID,
    db = Depends(get_db)
	) -> QuestionPackageResponseDTO:
	package_repository = QuestionPackageRepository(db)
	package_service = QuestionPackageService(package_repository)
	return package_service.create_question_package(package, player_id)


@router.patch("/{package_id}", response_model=QuestionPackageResponseDTO)
def update_question_package(
	package_id: int,
	package: QuestionPackageUpdateDTO,
	player_id: UUID,
	db = Depends(get_db)
) -> QuestionPackageResponseDTO:
	package_repository = QuestionPackageRepository(db)
	package_service = QuestionPackageService(package_repository)
	return package_service.update_question_package(package_id, package, player_id)


@router.delete("/{package_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question_package(
    package_id: int,
    player_id: UUID,
    db = Depends(get_db)
	) -> Response:
	package_repository = QuestionPackageRepository(db)
	package_service = QuestionPackageService(package_repository)
	package_service.delete_question_package(package_id, player_id)
	return Response(status_code=status.HTTP_204_NO_CONTENT)