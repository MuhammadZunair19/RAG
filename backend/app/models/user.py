"""User model per README §13.1."""

from sqlalchemy import Column, Integer, String, DateTime, func, Enum
from sqlalchemy.orm import relationship

from app.db.base import Base
import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default=UserRole.user.value)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    documents = relationship("Document", back_populates="uploaded_by_user")
    chats = relationship("Chat", back_populates="user")
