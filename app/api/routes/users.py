from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.users_schemas import UserCreate, UserResponse, Token
from utils import helpers
from database.database import get_db
from models import database_models
from fastapi.security import OAuth2PasswordRequestForm
from ..auth import oauth


router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(database_models.User).filter(database_models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    
    # Hash password
    hashed_password = helpers.hash_password(user.password)
    user.password = hashed_password

    # Create user
    new_user = database_models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login_user(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(database_models.User).filter(database_models.User.email == user_credentials.username).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
    
    if not helpers.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
    
    # Generate token
    access_token = oauth.create_access_token(data = {'user_id': user.id, 'role': user.role})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_user_me(current_user: UserResponse = Depends(oauth.get_current_user)):
    return current_user
