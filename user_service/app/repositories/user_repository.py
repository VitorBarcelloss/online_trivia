from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import User
from sqlalchemy.exc import (
    SQLAlchemyError,
    IntegrityError,
    DatabaseError,
    UserAlreadyExistsError
)


class UserRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, user: User) -> User:
        try:
            self.db.add(user)
            self.flush()
            self.refresh(user)
            
            return user
        except IntegrityError as exc:
            self.session.rollback()
            raise UserAlreadyExistsError() from exc
        except SQLAlchemyError as exc:
            self.session.rollback()
            raise DatabaseError() from exc
        
    def get_by_id(self, user_id: UUID) -> User | None:
        try:
            return self.db.get(User, user_id)
        except SQLAlchemyError as exc:
            raise DatabaseError() from exc
    
    def get_by_email(self, email: str) -> User | None:
        try:
            statement = select(User).where(User.email == email)
            
            return self.db.scalar(statement)
        except SQLAlchemyError as exc:
            raise DatabaseError() from exc
    
    def get_by_nickname(self, nickname: str) -> User | None:
        try:
            statement = select(User).where(User.nickname == nickname)
            
            return self.db.scalar(statement)
        except SQLAlchemyError as exc:
            raise DatabaseError() from exc
    
    def update(self, user: User) -> User:
        try:
            self.db.flush()
            self.db.refresh(user)
            
            return user
        except IntegrityError as exc:
            self.session.rollback()
            raise UserAlreadyExistsError() from exc
        except SQLAlchemyError as exc:
            self.session.rollback()
            raise DatabaseError() from exc
    
        