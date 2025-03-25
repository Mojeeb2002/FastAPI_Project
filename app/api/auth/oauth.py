from datetime import datetime, timedelta
from ...config.config import settings
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from ...models import database_models
from ...database.database import get_db
from ...schemas import users_schemas


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):
    to_encode = data.copy()

    # Add expiration time to token
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    # Encode token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")

        if user_id is None:
            raise credentials_exception
        
        user_id = int(user_id)
        role = payload.get("role")

        token_data = users_schemas.TokenData(user_id=user_id, role=role)
    except JWTError:
        raise credentials_exception
    
    return token_data


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    token = verify_token(token, credentials_exception)
    user = db.query(database_models.User).filter(database_models.User.id == token.user_id).first()

    if user is None:
        raise credentials_exception
    
    return user