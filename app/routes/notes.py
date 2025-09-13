from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.auth_utils import decode_access_token
from app.models.user import User
from app.models.note import Note, NoteStatus
import time
import random
from app.schemas.note import NoteResponse, NoteCreate
from app.utils.summarizer import summarize_text
from typing import List

router = APIRouter(prefix="/notes", tags=["notes"])
security = HTTPBearer()

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):

    payload = decode_access_token(creds.credentials)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.email == payload.get("sub")).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


def process_note(note_id:int, db: Session):

    note = db.query(Note).filter(Note.id == note_id).first()

    if not note:
        return
    
    note.status = NoteStatus.PROCESSING
    db.commit()

    try:
        note.summary = summarize_text(note.raw_text)
        note.status = NoteStatus.DONE
    except Exception:
        note.status = NoteStatus.FAILED
    finally:
        db.commit()


@router.post("/", response_model=NoteResponse)
def create_note(
                note_in: NoteCreate, 
                background_tasks: BackgroundTasks, 
                db: Session = Depends(get_db),
                user: User = Depends(get_current_user)):
    
    note = Note(raw_text = note_in.raw_text, owner_id = user.id)
    db.add(note)
    db.commit()
    db.refresh(note)

    background_tasks.add_task(process_note, note.id, db)

    return note


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(note_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):

    note = db.query(Note).filter(Note.id == note_id, Note.owner_id == user.id).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return note


@router.get("/", response_model=List[NoteResponse])
def list_all_notes(db: Session = Depends(get_db), user: User = Depends(get_current_user)):

    if user.role == "ADMIN":
        notes = db.query(Note).all()
    else:
        notes = db.query(Note).filter(Note.owner_id == user.id).all()

    return notes

