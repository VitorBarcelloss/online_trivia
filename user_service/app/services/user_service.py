from app.dtos.user import CreateUserDTO, LoginDTO, LoginResponseDTO, UserResponseDTO
import re

from user_service.app.core.exceptions import ServiceErrorMessage, UserException
from user_service.app.core.security import Security
import uuid

import phonenumbers
from phonenumbers import PhoneNumberFormat

from user_service.app.models.user import User
from user_service.app.repositories.user_repository import UserRepository

class UserService:
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def create_user_service(self,request_dto:CreateUserDTO):
        password_pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^\w\s]).{8,}$"
        raw_password = request_dto.password
        
        if not re.match(password_pattern, raw_password):
            raise UserException(ServiceErrorMessage.INVALID_PASSWORD_PATTERN)
        
        password_hash = Security.hash_password(raw_password)
        user_id = uuid.uuid4()
        
        if request_dto.phone:
            formatted_phone = self.format_phone_number(request_dto.phone)
        
        user = User(
            id=user_id,
            nickname=request_dto.nickname,
            name=request_dto.name,
            email=request_dto.email,
            password_hash=password_hash,
            phone=formatted_phone if request_dto.phone else None,
            birth_date=request_dto.birth_date | None,
            country=request_dto.country | None,
        )
        
        self.user_repository.create(user)
        
        if not user.created_at:
            self.user_repository.db.rollback()
            raise UserException(ServiceErrorMessage.USER_CREATION_FAILED)
        
        self.user_repository.db.commit()
        
        return UserResponseDTO(
            status_code=201,
            code="USER_CREATED",
        )
        
    def login_service(self, request_dto: LoginDTO):
        email = request_dto.email
        nickname = request_dto.nickname
        password = request_dto.password 
        is_guest = request_dto.is_guest | False
        
        if nickname and is_guest:
            access_token = Security.encode_token(uuid.uuid4(), nickname, is_guest)
                    
            return LoginResponseDTO(
                status_code=200,
                code="GUEST_LOGIN_SUCCESS",
                access_token=access_token
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
        
        access_token = Security.encode_token(user.id, user.nickname, is_guest)
        
        return LoginResponseDTO(
            status_code=200,
            code="LOGIN_SUCCESS",
            access_token=access_token
        )

    @staticmethod
    def format_phone_number(phone_number: str, country_code: str = "BR") -> str:
        try:
            parsed_number = phonenumbers.parse(phone_number, country_code)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError("Invalid phone number")
            formatted_number = phonenumbers.format_number(parsed_number, PhoneNumberFormat.E164)
            return formatted_number
        except phonenumbers.NumberParseException:
            raise ValueError("Invalid phone number format")
        
        