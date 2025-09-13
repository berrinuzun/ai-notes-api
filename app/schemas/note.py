from pydantic import BaseModel
from typing import Optional
from app.models.note import NoteStatus

class NoteCreate(BaseModel):
    raw_text: str

class NoteResponse(BaseModel):
    id: int
    raw_text: str
    summary: Optional[str]
    status: NoteStatus

    class Config:
        orm_mode = True

