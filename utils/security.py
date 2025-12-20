from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from crud.database import get_db
from models.models_db import Users
from fastapi import Depends, HTTPException
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
import logging
import os

# дані з .env
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="auth/login")


# затичка для помилки
logging.getLogger("passlib").setLevel(logging.ERROR)

# Налаштування хешування
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    """Перетворює пароль у хеш"""
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    """Порівнює пароль з хемош """
    return pwd_context.verify(plain_password, hashed_password)

# Налаштування jwt
def create_access_token(data: dict):
    """Створює JWT токен"""
    to_encode = data.copy()

    # час життя
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt

#отримуємо юзера
def get_current_user(token: str = Depends(OAUTH2_SCHEME),
                     db: Session = Depends(get_db)):

    credentials_exception = HTTPException(
        status_code=401,
        detail="Не знайдено користувача"
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Шукаємо в базі
    user = db.query(Users).filter(Users.id == user_id).first()

    if user is None:
        raise credentials_exception

    return user  # Повертаємо


