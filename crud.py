from sqlalchemy.orm import Session
import web.models as models, pydantic_validation

def get_user_by_login(db: Session, user_login: str)->Session.query:
    return db.query(models.User).filter(models.User.login == user_login).first()

def get_user_by_email(db: Session, user_email: str)->Session.query:
    return db.query(models.User).filter(models.User.email == user_email)

def get_all_users(db: Session, skip: int = 0, limit: int = 100)->Session.query:
    return db.query(models.User).offset(skip).limit(limit).all()

def get_item_by_id(db: Session, item_id: int)->Session.query:
    return db.query(models.Item).filter(models.Item.item_id == item_id).first()

def get_user_items(db:Session,user_id)->Session.query:
    return db.query(models.Item).filter(models.Item.item_owner == user_id).all()

def get_all_items(db: Session, skip: int = 0, limit: int = 100)->Session.query:
    return db.query(models.Item).offset(skip).limit(limit).all()

def add_item_to_cart(db: Session, item)->Session.query:
    new_item = models.Item(item_title=item.item_title,
                           item_description=item.item_description,
                           item_cost = item.item_cost,
                           item_image = item.item_image,
                           item_owner = item.item_owner)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

def create_user(db: Session, user: pydantic_validation.UserCreate)->models.User:
    new_user = models.User(login=user.login,
                           email = user.email,
                           password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def create_item(db: Session, item: pydantic_validation.ItemCreate)->models.Item:
    new_item = models.Item(item_title = item.item_title,
                           item_description = item.item_description,
                           item_cost = item.item_cost,
                           item_owner = item.item_owner)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

def create_shop(db: Session, shop)->models.Shop:
    new_shop = models.Shop(shop_title = shop.title,
                           shop_description = shop.description,
                           shop_cost = shop.cost,
                           shop_image = shop.image)
    db.add(new_shop)
    db.commit()
    db.refresh(new_shop)
    return new_shop