from typing import Optional, List
from pydantic import EmailStr
from app.repositories.user_repository import UserRepository
from app.models.user import User


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def create(self, username: str, hashed_password: str, name: Optional[str], email: Optional[str]) -> User:
        return self.repo.create(username=username, hashed_password=hashed_password, name=name, email=email)

    def get(self, user_id: int) -> Optional[User]:
        return self.repo.get(user_id)

    def list(self, search: Optional[str], status: Optional[bool], role_admin: Optional[bool], limit: int, offset: int) -> List[User]:
        return self.repo.list(search, status, role_admin, limit, offset)

    def update(self, user_id: int, name: Optional[str], email: Optional[EmailStr], is_active: Optional[bool], is_admin: Optional[bool]) -> Optional[User]:
        user = self.repo.get(user_id)
        if not user:
            return None
        return self.repo.update(user, name, email, is_active, is_admin)

    def delete(self, user_id: int) -> bool:
        user = self.repo.get(user_id)
        if not user:
            return False
        self.repo.delete(user)
        return True