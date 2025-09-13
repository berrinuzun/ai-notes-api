from fastapi import FastAPI
from database import Base, engine
from routes.auth import router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Notes API")

app.include_router(router)
