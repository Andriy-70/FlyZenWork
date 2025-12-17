from sqlalchemy.orm import Session
from models.models_db import Users
from schemas import users_schema as us
from utils.security import hash_password

""" Модуль для CRUD над таблицею користувачів """

def create_user(db: Session, user: us.RegisterUser):
    """ Реєстрація нового користувача з хешуванням пароля. """

    # Створюємо об'єкт моделі, перетворюючи типи Pydantic у типи SQLAlchemy
    new_user = Users(
        full_name = user.full_name,
        email = str(user.email),
        password_hash = hash_password(user.password) #
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()    # відкат
        raise e