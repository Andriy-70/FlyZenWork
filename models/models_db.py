from sqlalchemy import Column, Integer, String, TIMESTAMP, text
from crud.database import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True,nullable=False)
    password_hash = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

