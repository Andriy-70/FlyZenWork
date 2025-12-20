import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Завантажуємо дані з .env
load_dotenv()

# Отримуємо URL з оточення
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base() # модель для бд


def get_db():
    """ конект до базиданих"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()