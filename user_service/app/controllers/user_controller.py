from fastapi import APIRouter, Depends
from app.dtos.user import LoginResponseDTO, UpdateUserDTO, UpdateUserPasswordDTO, UserProfileResponseDTO, UserResponseDTO, CreateUserDTO, LoginDTO
from uuid import UUID
from app.core.security import Security
from user_service.app.database.database import get_db
from user_service.app.repositories.user_repository import UserRepository
from user_service.app.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

@router.post("/create", response_model=UserResponseDTO)
def create_user(request_dto:CreateUserDTO, db = Depends(get_db)):
    repository = UserRepository(db)
    service = UserService(repository)
    return service.create_user_service(request_dto)

@router.post("/update", response_model=UserResponseDTO)
def update_user(request_dto:UpdateUserDTO | UpdateUserPasswordDTO, user_id: UUID = Depends(Security.get_current_user)):
    pass

@router.post("/login", response_model=LoginResponseDTO)
def login(request_dto:LoginDTO, db = Depends(get_db)):
    repository = UserRepository(db)
    service = UserService(repository)
    return service.login_service(request_dto)

@router.get("/profile", response_model=UserProfileResponseDTO)
def user_profile(user_id: UUID = Depends(Security.get_current_user)):
    pass