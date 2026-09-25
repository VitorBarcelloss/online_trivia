from fastapi import APIRouter, Depends, status
from app.dtos.user import UpdateUserDTO, UpdateUserPasswordDTO, UserProfileResponseDTO, UserResponseDTO, CreateUserDTO
from uuid import UUID
from app.core.security import Security
from user_service.app.database.database import get_db
from user_service.app.repositories.user_repository import UserRepository
from user_service.app.services.user_service import UserService
from app.core.exceptions import UserException, ServiceErrorMessage

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

@router.post("/create", response_model=UserResponseDTO, status_code=status.HTTP_201_CREATED)
def create_user(
    request_dto:CreateUserDTO, 
    db = Depends(get_db)
    ):
    repository = UserRepository(db)
    service = UserService(repository)
    return service.create_user_service(request_dto)

@router.post("/update", response_model=UserResponseDTO)
def update_user(
    request_dto:UpdateUserDTO | UpdateUserPasswordDTO, 
    user_info: dict = Depends(Security.get_current_user), 
    db = Depends(get_db)
    ):
    if user_info['is_logged'] == False:
            raise UserException(ServiceErrorMessage.USER_NOT_LOGGED)
        
    repository = UserRepository(db)
    service = UserService(repository)
    return service.uspdate_user_service(request_dto, user_info['user_id'])

@router.get("/profile", response_model=UserProfileResponseDTO)
def user_profile(
    user_info: dict = Depends(Security.get_current_user), 
    db = Depends(get_db)
    ):
    if user_info['is_logged'] == False:
        raise UserException(ServiceErrorMessage.USER_NOT_LOGGED)
    
    repository = UserRepository(db)
    service = UserService(repository)
    return service.user_profile_service(user_info['user_id'])