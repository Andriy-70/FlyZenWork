from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from crud.database  import get_db
from models.models_db import Users
from utils.security import verify_password, create_access_token
from schemas import users_schema as us
from crud import users_db as crud

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
def login_user(user_data: us.LoginUser, db: Session = Depends(get_db)):

    user = db.query(Users).filter(Users.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний email або пароль"
        )

    # створення токена
    access_token = create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}