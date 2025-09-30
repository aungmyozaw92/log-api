from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.schemas.user import APIResponse, UserCreate, UserUpdate, UserResponse


router = APIRouter()


def get_user_service(db: Session = Depends(get_db)):
    return UserService(UserRepository(db))


@router.post("/", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate, svc: UserService = Depends(get_user_service)):
    # NOTE: In production, hash password here using your auth service
    user = svc.create(body.username, body.password, body.name, body.email)
    return APIResponse(success=True, message="User created", data={"user": UserResponse.model_validate(user).model_dump()})


@router.get("/{user_id}", response_model=APIResponse)
def get_user(user_id: int, svc: UserService = Depends(get_user_service)):
    user = svc.get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return APIResponse(success=True, message="User fetched", data={"user": UserResponse.model_validate(user).model_dump()})


@router.get("/", response_model=APIResponse)
def list_users(
    search: Optional[str] = Query(default=None),
    status: Optional[bool] = Query(default=None),
    role_admin: Optional[bool] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    svc: UserService = Depends(get_user_service),
):
    users = svc.list(search, status, role_admin, limit, offset)
    return APIResponse(success=True, message="Users fetched", data={"users": [UserResponse.model_validate(u).model_dump() for u in users]})


@router.patch("/{user_id}", response_model=APIResponse)
def update_user(user_id: int, body: UserUpdate, svc: UserService = Depends(get_user_service)):
    updated = svc.update(user_id, body.name, body.email, body.is_active, body.is_admin)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return APIResponse(success=True, message="User updated", data={"user": UserResponse.model_validate(updated).model_dump()})


@router.delete("/{user_id}", response_model=APIResponse)
def delete_user(user_id: int, svc: UserService = Depends(get_user_service)):
    ok = svc.delete(user_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return APIResponse(success=True, message="User deleted", data=None)


