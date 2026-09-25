from app.dtos.user import CreateUserDTO, UserResponseDTO, UserProfileResponseDTO, UpdateUserDTO, UpdateUserPasswordDTO
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
    
    def create_user_service(self,request_dto:CreateUserDTO) -> UserResponseDTO:
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
            code="USER_CREATED",
        )

        
    def user_profile_service(self, user_id: uuid.UUID) -> UserProfileResponseDTO:
        user = self.user_repository.get_by_id(user_id)
        
        if not user:
            raise UserException(ServiceErrorMessage.USER_DOES_NOT_EXISTS)
        
        user_dto = UserProfileResponseDTO(
            nickname=user.nickname,
            name=user.name,
            email=user.email,
            phone=user.phone,
            birth_date=user.birth_date,
            country=user.country
        )
        
        return user_dto
    
    def update_user_service(
        self, 
        request_dto: UpdateUserPasswordDTO | UpdateUserDTO, 
        user_id: uuid.UUID
        ) -> UserResponseDTO:
        
        request_type = request_dto.dto_type
        
        match request_type:
            case "update_general_info":
                data = request_dto.model_dump(exclude_unset=True)
                
                user = self.user_repository.get_by_id(user_id)
                
                if not user:
                    raise UserException(ServiceErrorMessage.USER_DOES_NOT_EXIST)

                old_updated_at = user.updated_at
                
                if "phone" in data:
                    data["phone"] = self.format_phone_number(data["phone"])
                
                for field, value in data.items():
                    setattr(user, field, value)
                
                user = self.user_repository.update(user)
                
                if user.updated_at == old_updated_at:
                    self.user_repository.db.rollback()
                    raise UserException(ServiceErrorMessage.USER_UPDATE_FAILED)
                
                self.user_repository.db.commit()
                
                return UserResponseDTO(
                        code="USER_UPDATED",
                    )                
                
            case "update_password":
                user = self.user_repository.get_by_id(user_id)
                                
                if not user:
                    raise UserException(ServiceErrorMessage.USER_DOES_NOT_EXIST)
                
                old_updated_at = user.updated_at
                old_password_hash = user.password_hash
                old_password = request_dto.old_password
                
                if request_dto.new_password != request_dto.confirm_password:
                    raise UserException(ServiceErrorMessage.PASSWORD_CONFIRMATION_MISMATCH)
                
                verified_password = Security.verify_password(old_password, old_password_hash)
                
                if not verified_password:
                    raise UserException(ServiceErrorMessage.INVALID_PASSWORD)
                
                new_password_hash = Security.hash_password(request_dto.new_password)
                
                if new_password_hash == old_password_hash:
                    raise UserException(ServiceErrorMessage.INVALID_PASSWORD)
                
                user.password_hash = new_password_hash
                
                user = self.user_repository.update(user)
                                
                if user.updated_at == old_updated_at or (new_password_hash == old_password_hash):
                    self.user_repository.db.rollback()
                    raise UserException(ServiceErrorMessage.USER_UPDATE_FAILED)
                
                self.user_repository.db.commit()
                
                return UserResponseDTO(
                        code="USER_UPDATED",
                    )                
                
            case _:
                raise UserException(ServiceErrorMessage.INVALID_UPDATE_REQUEST_TYPE)
            
        
        

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
        
        