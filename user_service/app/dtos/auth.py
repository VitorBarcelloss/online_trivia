from pydantic import BaseModel

class AuthCheckResponseDTO(BaseModel):
    code:str
    status:str
