from sqlalchemy import Column, Integer, String, TIMESTAMP, Enum, Text, ForeignKey, text
from crud.database import Base
import enum


class UserRole(str, enum.Enum):
    """ опис ролів """
    user = "user"
    admin = "admin"


class ProjectStatus(str, enum.Enum):
    """ опис статусів"""
    active = "active"
    closed = "closed"
    completed = "completed"

# опис таблиць
class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True,nullable=False)
    password_hash = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    role =  Column(Enum(UserRole), server_default="user", nullable=False)


class Projects(Base):
    __tablename__ = "projects"

    id_project = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description= Column(Text, nullable=False)
    status = Column(Enum(ProjectStatus), server_default="active", nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),nullable=False)