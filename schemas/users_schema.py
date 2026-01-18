from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal

"""
Схеми валідації даних користувача
"""

class RegisterUser(BaseModel):
    full_name: str
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: Literal['admin', 'user'] = 'user'

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool

#схеми для jwt
class Token(BaseModel):
    """ повертає сервер з успішного входу"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """витягнемо з розшифрованого токена"""
    user_id: Optional[int] = None