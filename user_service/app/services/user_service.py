import datetime
import re
import uuid

from sqlalchemy.exc import IntegrityError

from app.dtos.user import CreateUserDTO, UserResponseDTO, UserProfileResponseDTO, UpdateUserDTO, UpdateUserPasswordDTO

from app.core.exceptions import ServiceErrorMessage, UserException
from app.core.security import Security
import phonenumbers
from phonenumbers import PhoneNumberFormat

from app.models.user import User
from app.repositories.user_repository import UserRepository

class UserService:
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def create_user_service(self,request_dto:CreateUserDTO) -> UserResponseDTO:
        password_pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^\w\s]).{8,}$"
        raw_password = request_dto.password
        
        if not re.match(password_pattern, raw_password):
            raise UserException(ServiceErrorMessage.INVALID_PASSWORD_PATTERN)

        formatted_phone = None
        if request_dto.phone:
            try:
                formatted_phone = self.format_phone_number(request_dto.phone)
            except ValueError as exc:
                raise UserException(ServiceErrorMessage.INVALID_REQUEST) from exc

        email = str(request_dto.email).casefold()
        existing_response = self._existing_user_response(
            request_dto,
            email,
            formatted_phone,
        )
        if existing_response:
            return existing_response
        
        password_hash = Security().hash_password(raw_password)
        user_id = uuid.uuid4()
        
        user = User(
            id=user_id,
            nickname=request_dto.nickname,
            name=request_dto.name,
            email=email,
            password_hash=password_hash,
            phone=formatted_phone if request_dto.phone else None,
            birth_date=request_dto.birth_date or None,
            country=request_dto.country or None,
        )
        
        try:
            self.user_repository.create(user)
            self.user_repository.db.commit()
        except IntegrityError as exc:
            self.user_repository.db.rollback()
            existing = (
                self.user_repository.get_by_email(email)
                or self.user_repository.get_by_nickname(request_dto.nickname)
            )
            if existing:
                retry_response = self._existing_user_response(
                    request_dto,
                    email,
                    formatted_phone,
                )
                if retry_response:
                    return retry_response
                raise UserException(ServiceErrorMessage.USER_ALREADY_EXISTS) from exc
            raise
        
        return UserResponseDTO(
            code="USER_CREATED",
        )

        
    def user_profile_service(self, user_info: dict) -> UserProfileResponseDTO:
        if user_info["access_type"] != "access":
            raise UserException(ServiceErrorMessage.TOKEN_NOT_ALLOWED)

        if user_info['is_logged'] == False:
            raise UserException(ServiceErrorMessage.USER_NOT_LOGGED)

        if user_info["expires_at"] < datetime.datetime.now(datetime.timezone.utc):
            raise UserException(ServiceErrorMessage.USER_TOKEN_EXPIRED)

        user = self.user_repository.get_by_id(user_info['user_id'])
        
        if not user:
            raise UserException(ServiceErrorMessage.USER_DOES_NOT_EXIST)
        
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
        user_info: dict
        ) -> UserResponseDTO:
        if user_info["access_type"] != "access":
            raise UserException(ServiceErrorMessage.TOKEN_NOT_ALLOWED)

        if user_info['is_logged'] == False:
            raise UserException(ServiceErrorMessage.USER_NOT_LOGGED)

        if user_info["expires_at"] <  datetime.datetime.now(datetime.timezone.utc):
            raise UserException(ServiceErrorMessage.USER_TOKEN_EXPIRED)
        
        request_type = request_dto.dto_type
        
        match request_type:
            case "update_general_info":
                data = request_dto.model_dump(exclude_unset=True)
                data.pop("dto_type", None)
                
                user = self.user_repository.get_by_id(user_info['user_id'])
                
                if not user:
                    raise UserException(ServiceErrorMessage.USER_DOES_NOT_EXIST)

                if "phone" in data and data["phone"] is not None:
                    try:
                        data["phone"] = self.format_phone_number(data["phone"])
                    except ValueError as exc:
                        raise UserException(ServiceErrorMessage.INVALID_REQUEST) from exc
                
                for field, value in data.items():
                    setattr(user, field, value)
                
                try:
                    user = self.user_repository.update(user)
                    self.user_repository.db.commit()
                except IntegrityError as exc:
                    self.user_repository.db.rollback()
                    raise UserException(ServiceErrorMessage.USER_ALREADY_EXISTS) from exc
                
                return UserResponseDTO(
                        code="USER_UPDATED",
                    )                
                
            case "update_password":
                user = self.user_repository.get_by_id(user_info['user_id'])
                                
                if not user:
                    raise UserException(ServiceErrorMessage.USER_DOES_NOT_EXIST)
                
                old_password_hash = user.password_hash
                old_password = request_dto.old_password
                
                if request_dto.new_password != request_dto.confirm_password:
                    raise UserException(ServiceErrorMessage.PASSWORD_CONFIRMATION_MISMATCH)

                password_pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^\w\s]).{8,}$"
                if not re.match(password_pattern, request_dto.new_password):
                    raise UserException(ServiceErrorMessage.INVALID_PASSWORD_PATTERN)

                if Security().verify_password(request_dto.new_password, old_password_hash):
                    return UserResponseDTO(code="USER_UPDATED")
                
                verified_password = Security().verify_password(old_password, old_password_hash)
                
                if not verified_password:
                    raise UserException(ServiceErrorMessage.INVALID_PASSWORD)
                
                new_password_hash = Security().hash_password(request_dto.new_password)
                
                if new_password_hash == old_password_hash:
                    raise UserException(ServiceErrorMessage.INVALID_PASSWORD)
                
                user.password_hash = new_password_hash
                
                user = self.user_repository.update(user)
                                
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

    def _existing_user_response(
        self,
        request_dto: CreateUserDTO,
        email: str,
        formatted_phone: str | None,
    ) -> UserResponseDTO | None:
        by_email = self.user_repository.get_by_email(email)
        by_nickname = self.user_repository.get_by_nickname(request_dto.nickname)
        existing = by_email or by_nickname
        if existing is None:
            return None

        same_identity = (
            (by_email is None or by_email.id == existing.id)
            and (by_nickname is None or by_nickname.id == existing.id)
        )
        same_data = (
            existing.nickname == request_dto.nickname
            and existing.email.casefold() == email
            and existing.name == request_dto.name
            and existing.phone == formatted_phone
            and existing.birth_date == (request_dto.birth_date or None)
            and existing.country == (request_dto.country or None)
            and Security().verify_password(request_dto.password, existing.password_hash)
        )
        if same_identity and same_data:
            return UserResponseDTO(code="USER_CREATED")
        raise UserException(ServiceErrorMessage.USER_ALREADY_EXISTS)
        
        