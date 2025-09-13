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


def fake_summarizer(note_id: int, db: Session):

    note = db.query(Note).filter(Note.id == note_id).first()

    if not note:
        return
    
    note.status = NoteStatus.PROCESSING
    db.commit()

    time.sleep(3)

    if random.random() > 0.1:
        note.summary = note.raw_text[:50] + "..."
        note.status = NoteStatus.DONE
    else:
        note.status = NoteStatus.FAILED

    db.commit()


@router.post("/notes", response_model=NoteResponse)
def create_note(
                note_in: NoteCreate, 
                background_tasks: BackgroundTasks, 
                db: Session = Depends(get_db),
                user: User = Depends(get_current_user)):
    
    note = Note(raw_text = note_in.raw_text, owner_id = user.id)
    db.add(note)
    db.commit()
    db.refresh(note)

    background_tasks.add_task(fake_summarizer, note.id, db)

    return note


@router.get("/notes/{id}", response_model=NoteResponse)
def get_note(note_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):

    note = db.query(Note).filter(Note.id == note_id, Note.owner_id == user.id).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return note

