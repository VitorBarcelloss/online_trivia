from uuid import UUID
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.config import settings
from app.core.exceptions import SecurityErrorMessage, UserException
import jwt
from pwdlib import PasswordHash
import datetime
from datetime import timezone

class Security:
    http_beaerer = HTTPBearer()
    def __init__(self):
        self.password_hasher = PasswordHash.recommended()

    def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(http_beaerer),
    ) -> dict:
        token = credentials.credentials
        payload = self.decode_token(token)
        is_logged = payload.get("logged")
        access_type = payload.get("type")
        expires_at_claim = payload.get("expires_at")

        if not isinstance(expires_at_claim, str):
            raise UserException(SecurityErrorMessage.INVALID_JWT_TOKEN)

        try:
            expires_at = datetime.datetime.fromisoformat(expires_at_claim)
        except ValueError as exc:
            raise UserException(SecurityErrorMessage.INVALID_JWT_TOKEN) from exc

        if expires_at.tzinfo is None:
            raise UserException(SecurityErrorMessage.INVALID_JWT_TOKEN)
        
        user_id = payload.get("idt")
        
        if user_id == None or not isinstance(user_id, str):
            raise UserException(SecurityErrorMessage.INVALID_USER_TOKEN)
            
        try:
            UUID(user_id)
        except ValueError as exc:
            raise UserException(SecurityErrorMessage.INVALID_USER_TOKEN) from exc
        
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
            raise UserException(SecurityErrorMessage.INVALID_JWT_TOKEN)
        
        return payload
    
    @staticmethod
    def encode_token(user_id: UUID, nickname: str, is_guest: bool = False) -> str:
        access_expires_at = datetime.datetime.now(timezone.utc) + datetime.timedelta(minutes=15)
        refresh_expires_at = datetime.datetime.now(timezone.utc) + datetime.timedelta(days=7)
        
        access_payload = {
            "idt": str(user_id),
            "type": "access",
            "logged": not is_guest,
            "expires_at": str(access_expires_at)
        }
        
        refresh_payload = {
            "idt": str(user_id),
            "type": "refresh",
            "logged": not is_guest,
            "expires_at": str(refresh_expires_at)
        }
        
        access_token = jwt.encode(
            access_payload,
            settings.jwt_secret,
            algorithm="HS256"
        )
        
        refresh_token = jwt.encode(
            refresh_payload,
            settings.jwt_secret,
            algorithm="HS256"
        )
        
        return access_token, refresh_token
    
    def hash_password(self, password: str) -> str:
        return self.password_hasher.hash(password)
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        return self.password_hasher.verify(password, hashed_password)
        