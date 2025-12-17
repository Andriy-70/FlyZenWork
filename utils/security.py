import os
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import logging

# дані з .env
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


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
