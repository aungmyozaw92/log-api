from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.user import User
from typing import List

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()

    def create(self, username: str, hashed_password: str, name: str = None, email: str = None):
        user = User(
            username=username,
            password=hashed_password,
            name=name,
            email=email,
            is_active=True,
            is_admin=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_last_login(self, user: User):
        user.last_login = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get(self, user_id: int) -> Optional[User]:
        return self.db.get(User, user_id)

    def list(self, search: Optional[str], status: Optional[bool], role_admin: Optional[bool], limit: int, offset: int) -> List[User]:
        q = self.db.query(User)
        if search:
            like = f"%{search}%"
            q = q.filter((User.username.ilike(like)) | (User.name.ilike(like)) | (User.email.ilike(like)))
        if status is not None:
            q = q.filter(User.is_active == status)
        if role_admin is not None:
            q = q.filter(User.is_admin == role_admin)
        return q.order_by(User.created_at.desc()).limit(limit).offset(offset).all()

    def update(self, user: User, name: Optional[str], email: Optional[str], is_active: Optional[bool], is_admin: Optional[bool]) -> User:
        if name is not None:
            user.name = name
        if email is not None:
            user.email = email
        if is_active is not None:
            user.is_active = is_active
        if is_admin is not None:
            user.is_admin = is_admin
        user.updated_at = datetime.utcnow()
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()