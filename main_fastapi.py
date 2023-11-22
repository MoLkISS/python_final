from fastapi import Depends, FastAPI, HTTPException, Form, File, UploadFile
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
import web.models as models
import pydantic_validation
import crud
import requests
from web.models import Item
from typing import List 
import traceback

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

@app.post("/upload")
async def upload_product(item: pydantic_validation.ItemCreate, db: Session = Depends(get_db)):
    try:
        crud.create_item(db, item)
        return {"message": "Product uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add_to_cart")
def add_to_cart(request_data: pydantic_validation.CartBase, db: Session = Depends(get_db)):
    try:
        crud.add_item_to_cart(db=db, user_id=request_data.user_id, item_id=request_data.item_id)
    except Exception as e:
        traceback_str = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Error in crud: {str(e)}\n{traceback_str}")
    

@app.post("/remove-multiple-from-cart")
def remove_multiple_from_cart(selected_items: List[pydantic_validation.CartBase], db: Session = Depends(get_db)):
    try:
        # Удаляем каждый выбранный предмет из корзины
        for item_remove in selected_items:
            success = crud.remove_item_from_cart(db, item_remove.user_id, item_remove.item_id)
            if not success:
                raise HTTPException(status_code=404, detail=f"Item with ID {item_remove.item_id} not found in the user's cart")

        return {"detail": "Selected items successfully removed from the cart"}
    except Exception as e:
        traceback_str = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Something went wrong: {str(e)}\n{traceback_str}")


@app.post("/add_review")
def create_review(review: pydantic_validation.ReviewCreate, db: Session = Depends(get_db)):
    try:

        crud.create_review(db=db, review=review)

        return {"detail": "Review created successfully"}
    except Exception as e:
        # Handle any exceptions and return an appropriate response
        raise HTTPException(status_code=500, detail=f"Something went wrong: {str(e)}")


@app.get("/user/cart")
def user_cart(user_id: int, db: Session = Depends(get_db)):
    return crud.get_cart_items_by_user(db=db, user_id=user_id)

@app.get("/users/", response_model=list[pydantic_validation.User])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_all_users(db)
    return users

@app.get("/users/{login}", response_model=pydantic_validation.User)
def get_certain_user(login, db: Session = Depends(get_db)):
    return crud.get_user_by_login(db, login)

@app.get("/items/")
def get_all_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_all_items(db=db, skip=skip, limit=limit)
    print(items)
    data = []
    for item in items:
        item_data = {
            'item_id': item.item_id,
            'item_title': item.item_title,
            'item_description': item.item_description,
            'item_cost': item.item_cost,
            'item_image': item.item_image
        }
        data.append(item_data)

    return data

@app.get("/user/items/{user_id}", response_model=list[pydantic_validation.Item])
def get_user_works(user_id, db: Session = Depends(get_db)):
    return crud.get_user_items(db, user_id)

@app.get("/item/{item_id}/", response_model=pydantic_validation.Item)
def get_item(item_id:int, db: Session = Depends(get_db)):
    return crud.get_item_by_id(db, item_id)

@app.get("/get_reviews")
def fetch_reviews(db: Session = Depends(get_db)):
    reviews = crud.get_reviews_with_user_login(db=db)
    return reviews

@app.get('/get_user_data/{user_id}')
def fetch_user_data(user_id: int, db: Session = Depends(get_db)):
    user_data = crud.get_user_data(db, user_id)
    if user_data:
        return user_data
    else:
        return {"detail": "User not found"}