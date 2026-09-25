from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Literal

class CreateUserDTO(BaseModel):
    nickname:str = Field(min_length=3)
    name:str
    email: EmailStr
    password: str = Field(min_length=6, max_length=20)
    phone: str | None = None
    birthdate: date | None = None
    country: str | None = None

class UpdateUserDTO(BaseModel):
    dto_type: Literal["update_general_info"]
    nickname:str | None = None
    email:EmailStr | None = None
    phone:str | None = None
    
class UpdateUserPasswordDTO(BaseModel):
    dto_type: Literal["update_password"]
    old_password:str
    new_password:str
    confirm_password:str
    
class UserProfileResponseDTO(BaseModel):
    nickname:str
    name:str
    email: EmailStr
    phone: str | None = None
    birthdate: date | None = None
    country: str | None = None
    
class LoginDTO(BaseModel):
    is_guest: bool = False
    nickname:str | None
    email:EmailStr | None
    password:str

class LoginResponseDTO(BaseModel):
    status_code:int = Field(ge=200, lt=300)
    code:str
    access_token:str
    
class UserResponseDTO(BaseModel):
    code:str

    

    