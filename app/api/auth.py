from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, UserResponse, Token, APIResponse, LoginRequest, ProfileResponse
from app.deps import get_auth_service, get_current_user
from app.repositories.user_repository import UserRepository
from app.core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/register", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, service = Depends(get_auth_service)):
    try:
        created = service.register(user.username, user.password, name=user.name, email=user.email)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return APIResponse(success=True, message="User registered", data={"user": UserResponse.model_validate(created).model_dump()})

@router.post("/login", response_model=APIResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), service = Depends(get_auth_service), db: Session = Depends(get_db)):
    try:
        user = service.authenticate(form_data.username, form_data.password)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = service.create_token(user.username)
    # update last_login
    UserRepository(db).update_last_login(user)
    return APIResponse(success=True, message="Login successful", data={
        "token": {"access_token": token, "token_type": "bearer"},
        "user": UserResponse.model_validate(user).model_dump()
    })

@router.get("/profile", response_model=APIResponse)
def profile(current_user = Depends(get_current_user)):
    return APIResponse(success=True, message="Profile fetched", data={"user": ProfileResponse.model_validate(current_user).model_dump()})