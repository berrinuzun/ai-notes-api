from app.database import Base
from sqlalchemy import Column, Integer, String, Enum, DateTime, func
import enum
from sqlalchemy.orm import relationship

class Role(str, enum.Enum):
    ADMIN = "ADMIN"
    AGENT = "AGENT"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(Role), default=Role.AGENT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    notes = relationship("Note", back_populates="owner")