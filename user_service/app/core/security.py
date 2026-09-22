from uuid import UUID
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.config import settings
from app.core.exceptions import SecurityErrorMessage, APIException
import jwt

class Security:
    security = HTTPBearer

    def get_current_user(self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> UUID:
        token = credentials.credentials
        payload = self.decode_token(token)
        is_logged = payload.get("rnd") != None
        
        user_id = payload.get("idt")
        
        if user_id == None or user_id is not isinstance(UUID):
            APIException(SecurityErrorMessage.INVALID_USER_TOKEN)
        
        return user_id, is_logged
    
    @staticmethod
    def decode_token(token):
        try:
            payload = jwt.decode(
                settings.jwt_token, 
                algorithms="utf-8"
                )
        except jwt.exceptions.InvalidTokenError:
            raise APIException(SecurityErrorMessage.INVALID_JWT_TOKEN)
        
        return payload
        