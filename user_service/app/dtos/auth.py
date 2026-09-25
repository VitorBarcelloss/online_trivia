from pydantic import BaseModel, EmailStr, Field

class LoginDTO(BaseModel):
    is_guest: bool = False
    nickname:str | None
    email:EmailStr | None
    password:str

class LoginResponseDTO(BaseModel):
    status_code:int = Field(ge=200, lt=300)
    code:str
    access_token:str
    refresh_token:str
    
class RefreshResponseDTO(BaseModel):
    status_code:int = Field(ge=200, lt=300)
    code:str