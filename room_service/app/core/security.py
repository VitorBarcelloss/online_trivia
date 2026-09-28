
import secrets
from app.core.config import settings
from pwdlib import PasswordHash

class Security:
    def __init__(self):
        self.room_code_length = settings.room_code_length
        self.room_code_alphabet = settings.room_code_alphabet
        self.password_hasher = PasswordHash.recommended()   

    def generate_room_code(self) -> str:
        return "".join(
            secrets.choice(self.room_code_alphabet) 
            for _ in range(self.room_code_length)
            )

    def hash_password(self, password: str) -> str:
        return self.password_hasher.hash(password)
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        return self.password_hasher.verify(password, hashed_password)