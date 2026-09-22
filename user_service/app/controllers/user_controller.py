from fastapi import APIRouter, Depends
from app.dtos.user import UpdateUserDTO, UpdateUserPasswordDTO, UserProfileResponseDTO, UserResponseDTO, CreateUserDTO, LoginDTO
from uuid import UUID
from app.core.security import Security

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

@router.post("/create", response_model=CreateUserDTO)
def create_user(request_dto:UserResponseDTO):
    pass

@router.post("/update", response_model=UpdateUserDTO | UpdateUserPasswordDTO)
def update_user(request_dto:UserResponseDTO, user_id: UUID = Depends(Security.get_current_user)):
    pass

@router.post("/login", response_model=LoginDTO)
def login(request_dto:UserResponseDTO):
    pass

@router.get("/profile", response_model=UserProfileResponseDTO)
def user_profile(user_id: UUID = Depends(Security.get_current_user)):
    pass