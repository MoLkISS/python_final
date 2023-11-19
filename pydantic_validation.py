from pydantic import BaseModel

class UserBase(BaseModel):
    login: str
    email: str

class ItemBase(BaseModel):
    item_title: str
    item_description: str
    item_image: str
    item_cost: int

class CartBase(BaseModel):
    item_id: int
    user_id: int

class ItemCreate(ItemBase):
    item_owner: int

class Item(ItemBase):
    item_id: int
    item_owner: int

    class Config:
        orm_mode: True

class UserCreate(UserBase):
    password: str

class User(UserBase):
    user_id: int
    user_items: list[Item] = []

    class Config:
        orm_mode: True

class ItemRemove(BaseModel):
    item_id: int
    user_id: int