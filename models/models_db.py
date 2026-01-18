from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Enum, Text, ForeignKey, text
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

class ProjectStage(Base):
    __tablename__ = "project_stages"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id_project", ondelete="CASCADE"), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, default=0) # Порядок етапу (1-й, 2-й...)
    is_completed = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class RequestStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

# Таблиця для запитів на вступ у команду
class ProjectRequests(Base):
    __tablename__ = "project_requests"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id_project", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(RequestStatus), server_default="pending", nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))