from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, user: User) -> User:
        self.db.add(user)
        self.flush()
        self.refresh(user)
        
        return user
    
    def get_by_id(self, user_id: UUID) -> User | None:
        return self.db.get(User, user_id)
    
    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        
        return self.db.scalar(statement)
    
    def get_by_nickname(self, nickname: str) -> User | None:
        statement = select(User).where(User.nickname == nickname)
        
        return self.db.scalar(statement)
    
    def update(self, user: User) -> User:
        self.db.flush()
        self.db.refresh(user)
        
        return user
    
    
        