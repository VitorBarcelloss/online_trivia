from uuid import UUID

from fastapi import APIRouter, Depends
from app.database.database import get_db

from app.dtos.question_package import QuestionPackageDTO
from app.repositories.question_package_repository import QuestionPackageRepository
from app.services.question_package_service import QuestionPackageService

router = APIRouter(prefix="/question-packages", tags=["Question Packages"])


@router.get("/list", response_model=list[QuestionPackageDTO])
def get_question_packages(
    player_id: UUID | None = None,
    db = Depends(get_db)
    ) -> list[QuestionPackageDTO]:
	package_repository = QuestionPackageRepository(db)
	package_service = QuestionPackageService(package_repository)
	return package_service.get_question_packages(player_id)



@router.get("/{package_id}", response_model=QuestionPackageDTO)
def get_question_package__by_id(
	package_id: int,
	player_id: UUID | None = None,
	db = Depends(get_db)
) -> QuestionPackageDTO:
	package_repository = QuestionPackageRepository(db)
	package_service = QuestionPackageService(package_repository)
	return package_service.get_question_package__by_id_service(package_id, player_id)


@router.post("", response_model=QuestionPackageDTO)
def create_question_package(
    package: QuestionPackageDTO,
    player_id: UUID,
    db = Depends(get_db)
    ) -> QuestionPackageDTO:
	package_repository = QuestionPackageRepository(db)
	package_service = QuestionPackageService(package_repository)
	return package_service.create_question_package(package, player_id)


@router.put("/{package_id}", response_model=QuestionPackageDTO)
def update_question_package(
	package_id: int,
	package: QuestionPackageDTO,
	player_id: UUID,
	db = Depends(get_db)
) -> QuestionPackageDTO:
	package_repository = QuestionPackageRepository(db)
	package_service = QuestionPackageService(package_repository)
	return package_service.update_question_package(package_id, package, player_id)


@router.delete("/{package_id}")
def delete_question_package(
    package_id: int,
    player_id: UUID,
    db = Depends(get_db)
    ) -> None:
	package_repository = QuestionPackageRepository(db)
	package_service = QuestionPackageService(package_repository)
	package_service.delete_question_package(package_id, player_id)