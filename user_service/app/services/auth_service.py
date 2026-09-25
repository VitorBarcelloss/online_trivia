from app.dtos.auth import LoginResponseDTO, LoginDTO, RefreshResponseDTO
from app.core.security import Security
import uuid
from app.core.exceptions import UserException, ServiceErrorMessage
from app.repositories.user_repository import UserRepository
import datetime

class AuthService:
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
 
    def login_service(self, request_dto: LoginDTO) -> LoginResponseDTO:
        email = request_dto.email
        nickname = request_dto.nickname
        password = request_dto.password 
        is_guest = request_dto.is_guest | False
        
        if nickname and is_guest:
            access_token, refresh_token = Security.encode_token(uuid.uuid4(), nickname, is_guest)
                    
            return LoginResponseDTO(
                status_code=200,
                code="GUEST_LOGIN_SUCCESS",
                access_token=access_token,
                refresh_token=refresh_token
            )
        
        user = (
            self.user_repository.get_by_email(email) 
            if email else self.user_repository.get_by_nickname(nickname)
            )
        
        if not user:
            raise UserException(ServiceErrorMessage.INVALID_USERNAME)
        
        verified_password = Security.verify_password(password, user.password_hash)
        
        if not verified_password:
            raise UserException(ServiceErrorMessage.INVALID_PASSWORD)
        
        access_token, refresh_token = Security.encode_token(user.id, user.nickname, is_guest)
        
        return LoginResponseDTO(
            status_code=200,
            code="LOGIN_SUCCESS",
            access_token=access_token,
            refresh_token=refresh_token
        )
        
    def refresh_service(self, user_info: dict) -> RefreshResponseDTO:
        is_guest = not user_info.get("is_logged")
        access_type = user_info.get("access_type")
        expires_at = user_info.get("expires_at")
        user_id = user_info.get("user_id")
        
        if  is_guest:
            return RefreshResponseDTO(
                status_code=200,
                code="GUEST_AUTH_SUCCEDED",
            )
        
        if access_type != "refresh":
            raise UserException(ServiceErrorMessage.AUTH_FAILED)
        
        if expires_at > datetime.now():
            raise UserException(ServiceErrorMessage.TOKEN_EXPIRED)
        
        user = self.user_repository.get_by_id(user_id)
        
        if not user:
            raise UserException(ServiceErrorMessage.USER_DOES_NOT_EXIST)
        
        return RefreshResponseDTO(
            status_code=200,
            code="REFRESH_AUTH_SUCCEDED"
        )
            