from fastapi import APIRouter, Depends
from app.dtos.auth import LoginDTO, LoginResponseDTO, RefreshResponseDTO
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.database.database import get_db
from app.core.security import Security

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

@router.post("/login", response_model=LoginResponseDTO)
def login(
    request_dto:LoginDTO, 
    db = Depends(get_db)
    ):
    repository = UserRepository(db)
    service = AuthService(repository)
    return service.login_service(request_dto)

@router.post("/refresh", response_model=RefreshResponseDTO)
def refresh(
    user_info: dict = Depends(Security.get_current_user),
    db = Depends(get_db)
):
    repository = UserRepository(db)
    service = AuthService(repository)
    return service.refresh_service(user_info)