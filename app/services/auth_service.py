from app.core import security
from typing import Optional
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def register(self, username: str, password: str, name: Optional[str] = None, email: Optional[str] = None):
        existing = self.user_repo.get_by_username(username)
        if existing:
            # In a real app, raise an HTTPException in the route layer
            raise ValueError("Username already exists")
        hashed = security.hash_password(password)
        return self.user_repo.create(username, hashed, name=name, email=email)

    def authenticate(self, username: str, password: str):
        user = self.user_repo.get_by_username(username)
        if not user:
            raise ValueError("Invalid credentials")
        if not security.verify_password(password, user.password):
            raise ValueError("Invalid credentials")
        return user

    def create_token(self, username: str) -> str:
        return security.create_access_token(username)


