from pydantic import BaseModel, EmailStr
from app.models.user import Role

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: Role = Role.AGENT



