from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
import models, pydantic_validation, crud

models.Base.metadata.create_all(bind_engine)
models.Base.metadata.create_all(bind=engine)
