
import secrets

from pwdlib import PasswordHash

class Security:
    def __init__(self):
        self.room_code_length = 6  
        self.room_code_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
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