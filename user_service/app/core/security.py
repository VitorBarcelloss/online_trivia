from uuid import UUID
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.config import settings
from app.core.exceptions import SecurityErrorMessage, APIException
import jwt
from pwdlib import PasswordHash
import datetime
from datetime import timezone

class Security:
    security = HTTPBearer
    password_hasher = PasswordHash.Recommended()

    def get_current_user(self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> dict:
        token = credentials.credentials
        payload = self.decode_token(token)
        is_logged = payload.get("logged")
        access_type = payload.get("type")
        expires_at = payload.get("expires_at")
        
        user_id = payload.get("idt")
        
        if user_id == None or user_id is not isinstance(UUID):
            APIException(SecurityErrorMessage.INVALID_USER_TOKEN)
        
        return {
            "user_id": user_id, 
            "is_logged": is_logged,
            "access_type": access_type,
            "expires_at": expires_at
            }
    
    @staticmethod
    def decode_token(token):
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret, 
                algorithms="HS256"
                )
        except (jwt.exceptions.InvalidTokenError, ValueError):
            raise APIException(SecurityErrorMessage.INVALID_JWT_TOKEN)
        
        return payload
    
    @staticmethod
    def encode_token(user_id: UUID, nickname: str, is_guest: bool = False) -> str:
        access_expires_at = datetime.now(timezone.utc) + datetime.timedelta(minutes=15)
        refresh_expires_at = datetime.now(timezone.utc) + datetime.timedelta(days=7)
        
        access_payload = {
            "idt": str(user_id),
            "type": "access",
            "logged": not is_guest,
            "expires_at": access_expires_at
        }
        
        refresh_payload = {
            "idt": str(user_id),
            "type": "refresh",
            "logged": not is_guest,
            "expires_at": refresh_expires_at
        }
        
        access_token = jwt.encode(
            access_payload,
            settings.jwt_secret,
            algorithm="HS256",
            exp=access_expires_at
        )
        
        refresh_token = jwt.encode(
            refresh_payload,
            settings.jwt_secret,
            algorithm="HS256",
            exp=refresh_expires_at
        )
        
        return access_token, refresh_token
    
    def hash_password(self, password: str) -> str:
        return self.password_hasher.hash(password)
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        return self.password_hasher.verify(password, hashed_password)
        