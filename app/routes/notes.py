from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.auth.auth_utils import decode_access_token
from app.models.user import User
from app.models.note import Note, NoteStatus
import time
import random
from app.schemas.note import NoteResponse, NoteCreate, NoteUpdate
from app.utils.summarizer import summarize_text
from typing import List
import logging

router = APIRouter(prefix="/notes", tags=["notes"])
security = HTTPBearer()

logger = logging.getLogger(__name__)

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):

    payload = decode_access_token(creds.credentials)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.email == payload.get("sub")).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


def process_note(note_id:int):

    db = SessionLocal()

    try:
        note = db.query(Note).filter(Note.id == note_id).first()

        if not note:
            logger.warning(f"Note {note_id} not found")
            return
        
        if note.status == NoteStatus.DONE:
            logger.info(f"Note {note_id} already processed")
            return
        
        if note.status == NoteStatus.PROCESSING:
            logger.info(f"Note {note_id} already being processed")
            return
        
        logger.info(f"Starting processing note {note_id}")
        note.status = NoteStatus.PROCESSING
        db.commit()

        try:
            note.summary = summarize_text(note.raw_text)
            note.status = NoteStatus.DONE
            logger.info(f"Successfully processed note {note_id}")
        except Exception as e:
            note.status = NoteStatus.FAILED
            logger.error(f"Failed to process note {note_id}: {str(e)}")
        finally:
            db.commit()

    except Exception as e:
        logger.error(f"Database error processing note {note_id}: {str(e)}")
        db.rollback()
    finally:
        db.close()


@router.post("/", response_model=NoteResponse)
def create_note(
                note_in: NoteCreate, 
                background_tasks: BackgroundTasks, 
                db: Session = Depends(get_db),
                user: User = Depends(get_current_user)):
    
    try:
        note = Note(raw_text = note_in.raw_text, owner_id = user.id)
        db.add(note)
        db.commit()
        db.refresh(note)

        background_tasks.add_task(process_note, note.id)

        return note
    
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create note: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create note")


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(note_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):

    note = db.query(Note).filter(Note.id == note_id)

    if user.role != "ADMIN":
        note = note.filter(Note.owner_id == user.id)

    note = note.first()

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

@router.put("/{note_id}", response_model=NoteResponse)
def update_note(
                note_id: int,
                note_in: NoteUpdate,
                background_tasks: BackgroundTasks,
                db: Session = Depends(get_db),
                user = Depends(get_current_user)
):
    
    try:
        note = db.query(Note).filter(Note.id == note_id).first()

        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        if user.role != "ADMIN" and note.owner_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this note.")
        
        note.raw_text = note_in.raw_text
        note.status = NoteStatus.QUEUED
        note.summary = None
        db.commit()
        db.refresh(note)

        background_tasks.add_task(process_note, note.id)

        logger.info(f"Updated note {note_id}")

        return note
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update note {note_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update note")


@router.delete("/{note_id}", status_code=204)
def delete_note(
                note_id: int,
                db: Session = Depends(get_db),
                user = Depends(get_current_user)
):
    
    try: 
        note = db.query(Note).filter(Note.id == note_id).first()

        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        if user.role != "ADMIN" and note.owner_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this note")
        
        db.delete(note)
        db.commit()
        logger.info(f"Deleted note {note_id}")

        return None
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete note {note_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete note")







