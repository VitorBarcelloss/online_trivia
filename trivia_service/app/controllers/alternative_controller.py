from uuid import UUID

from fastapi import APIRouter, Depends
from app.database.database import get_db
from app.dtos.alternative import AlternativeDTO
from app.repositories.alternative_repository import AlternativeRepository
from app.services.alternative_service import AlternativeService

router = APIRouter(prefix="/alternatives", tags=["Alternatives"])


@router.get("/all", response_model=list[AlternativeDTO])
def get_all_alternatives(
	question_id: int,
	player_id: UUID | None = None,
	db = Depends(get_db)
) -> list[AlternativeDTO]:
	alternative_repository = AlternativeRepository(db)
	alternative_service = AlternativeService(alternative_repository)
	return alternative_service.get_alternatives(question_id, player_id)


@router.get("/{alternative_id}", response_model=AlternativeDTO)
def get_alternative(
	alternative_id: int,
	player_id: UUID | None = None,
	db = Depends(get_db)
) -> AlternativeDTO:
	alternative_repository = AlternativeRepository(db)
	alternative_service = AlternativeService(alternative_repository)
	return alternative_service.get_alternative(alternative_id, player_id)


@router.post("/create", response_model=AlternativeDTO)
def create_alternative(alternative: AlternativeDTO, player_id: UUID, db = Depends(get_db)) -> AlternativeDTO:
	alternative_repository = AlternativeRepository(db)
	alternative_service = AlternativeService(alternative_repository)
	return alternative_service.create_alternative(alternative, player_id)

@router.put("/update/{alternative_id}", response_model=AlternativeDTO)
def update_alternative(
	alternative_id: int,
	alternative: AlternativeDTO,
	player_id: UUID,
	db = Depends(get_db)
) -> AlternativeDTO:
	alternative_repository = AlternativeRepository(db)
	alternative_service = AlternativeService(alternative_repository)
	return alternative_service.update_alternative(alternative_id, alternative, player_id)


@router.delete("/delete/{alternative_id}")
def delete_alternative(alternative_id: int, player_id: UUID, db = Depends(get_db)) -> None:
	alternative_repository = AlternativeRepository(db)
	alternative_service = AlternativeService(alternative_repository)
	alternative_service.delete_alternative(alternative_id, player_id)