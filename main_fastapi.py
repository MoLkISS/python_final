from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
import web.models as models
import pydantic_validation
import crud

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/create", response_model=pydantic_validation.User)
def create_user(user:pydantic_validation.UserCreate, db: Session = Depends(get_db)):
    new_user = crud.get_user_by_login(db, user_login=user.login)

    if new_user:
        raise HTTPException(status_code=400, detail="Login is alredy taken by another user.")
    return crud.create_user(db=db, user=user)

@app.post("/item/create/", response_model=pydantic_validation.Item)
def create_item(item: pydantic_validation.ItemCreate, db: Session=Depends(get_db)):
    return crud.create_item(db, item=item)

@app.get("/users/", response_model=list[pydantic_validation.User])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_all_users(db)
    return users

@app.get("/users/{login}", response_model=pydantic_validation.User)
def get_certain_user(login, db: Session = Depends(get_db)):
    return crud.get_user_by_login(db, login)

@app.get("/items/", response_model=list[pydantic_validation.Item])
def get_all_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_all_items(db)

@app.get("/user/items/{user_id}", response_model=list[pydantic_validation.Item])
def get_user_works(user_id, db: Session = Depends(get_db)):
    return crud.get_user_items(db, user_id)

@app.get("/item/{item_id}/", response_model=pydantic_validation.Item)
def get_work(item_id:int, db: Session = Depends(get_db)):
    return crud.get_item_by_id(db, item_id)