from sqlalchemy.orm import Session
from datetime import datetime
from app.models.user import User


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