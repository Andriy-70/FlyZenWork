from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from crud.database  import get_db
from models.models_db import Users
from schemas import users_schema as us
from crud import users_db as crud
from utils.security import get_current_user, hash_password, verify_password, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user_data: us.RegisterUser, db: Session = Depends(get_db)):
    """ Ендпоінт для реєстрації нового користувача """

    #перевірка на дубліка email
    existing_user = db.query(Users).filter(Users.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Користувач з таким email вже існує"
        )

    new_user = crud.create_user(db, user_data)

    return new_user

@router.post("/login", status_code=status.HTTP_200_OK, response_model=us.Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(Users).filter(Users.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний email або пароль"
        )

    # створення токена
    access_token = create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=us.UserResponse)
def read_users_me(current_user: Users = Depends(get_current_user)):
    return current_user


@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(
        pass_data: us.ChangePassword,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    """ Зміна пароля: перевірка старого + хешування нового """

    # 1. Перевіряємо, чи старий пароль правильний
    if not verify_password(pass_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Старий пароль введено неправильно"
        )

    # 2. Перевіряємо, щоб новий пароль не був таким самим, як старий
    if pass_data.old_password == pass_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Новий пароль не може співпадати зі старим"
        )

    # 3. Хешуємо новий пароль і зберігаємо
    current_user.password_hash = hash_password(pass_data.new_password)
    db.commit()

    return {"message": "Пароль успішно змінено"}