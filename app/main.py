from fastapi import FastAPI
from app.database import Base, engine
from app.routes import auth, notes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Notes API")

app.include_router(auth.router)
app.include_router(notes.router)
