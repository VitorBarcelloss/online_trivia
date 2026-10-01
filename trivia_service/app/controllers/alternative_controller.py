from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from app.database.database import get_db
from app.dtos.alternative import AlternativeCreateDTO, AlternativeResponseDTO, AlternativeUpdateDTO
from app.repositories.alternative_repository import AlternativeRepository
from app.services.alternative_service import AlternativeService

router = APIRouter(prefix="/alternatives", tags=["Alternatives"])


@router.get("", response_model=list[AlternativeResponseDTO])
def get_all_alternatives(
	question_id: int,
	player_id: UUID | None = None,
	db = Depends(get_db)
) -> list[AlternativeResponseDTO]:
	alternative_repository = AlternativeRepository(db)
	alternative_service = AlternativeService(alternative_repository)
	return alternative_service.get_alternatives(question_id, player_id)


@router.get("/{alternative_id}", response_model=AlternativeResponseDTO)
def get_alternative(
	alternative_id: int,
	player_id: UUID | None = None,
	db = Depends(get_db)
) -> AlternativeResponseDTO:
	alternative_repository = AlternativeRepository(db)
	alternative_service = AlternativeService(alternative_repository)
	return alternative_service.get_alternative(alternative_id, player_id)


@router.post("", response_model=AlternativeResponseDTO, status_code=status.HTTP_201_CREATED)
def create_alternative(alternative: AlternativeCreateDTO, player_id: UUID, db = Depends(get_db)) -> AlternativeResponseDTO:
	alternative_repository = AlternativeRepository(db)
	alternative_service = AlternativeService(alternative_repository)
	return alternative_service.create_alternative(alternative, player_id)

@router.patch("/{alternative_id}", response_model=AlternativeResponseDTO)
def update_alternative(
	alternative_id: int,
	alternative: AlternativeUpdateDTO,
	player_id: UUID,
	db = Depends(get_db)
) -> AlternativeResponseDTO:
	alternative_repository = AlternativeRepository(db)
	alternative_service = AlternativeService(alternative_repository)
	return alternative_service.update_alternative(alternative_id, alternative, player_id)


@router.delete("/{alternative_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alternative(alternative_id: int, player_id: UUID, db = Depends(get_db)) -> Response:
	alternative_repository = AlternativeRepository(db)
	alternative_service = AlternativeService(alternative_repository)
	alternative_service.delete_alternative(alternative_id, player_id)
	return Response(status_code=status.HTTP_204_NO_CONTENT)