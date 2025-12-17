from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal

"""
Схеми валідації даних користувача
"""

class LoginUser(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class RegisterUser(BaseModel):
    full_name: str
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: Literal['admin', 'user'] = 'user'

#схеми для jwt
class Token(BaseModel):
    """ повертає сервер з успішного входу"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """витягнемо з розшифрованого токена"""
    user_id: Optional[int] = None