from uuid import UUID
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.config import settings
from app.core.exceptions import SecurityErrorMessage, APIException
import jwt
from pwdlib import PasswordHash

class Security:
    security = HTTPBearer
    password_hasher = PasswordHash.Recommended()

    def get_current_user(self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> UUID:
        token = credentials.credentials
        payload = self.decode_token(token)
        is_logged = payload.get("logged") == True
        
        user_id = payload.get("idt")
        
        if user_id == None or user_id is not isinstance(UUID):
            APIException(SecurityErrorMessage.INVALID_USER_TOKEN)
        
        return user_id, is_logged
    
    @staticmethod
    def decode_token(token):
        try:
            payload = jwt.decode(
                token,
                settings.jwt_token, 
                algorithms="HS256"
                )
        except (jwt.exceptions.InvalidTokenError, ValueError):
            raise APIException(SecurityErrorMessage.INVALID_JWT_TOKEN)
        
        return payload
    
    @staticmethod
    def encode_token(user_id: UUID, nickname: str, is_guest: bool = False) -> str:
        payload = {
            "idt": str(user_id),
            "nick": nickname,
            "logged": not is_guest,
        }
        
        token = jwt.encode(
            payload,
            settings.jwt_token,
            algorithm="HS256"
        )
        
        return token
    
    def hash_password(self, password: str) -> str:
        return self.password_hasher.hash(password)
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        return self.password_hasher.verify(password, hashed_password)
        