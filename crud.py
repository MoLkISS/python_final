from sqlalchemy.orm import Session, joinedload
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

def add_item_to_cart(db: Session, user_id: int, item_id: int):
    new_cart_item = models.Cart(user_id=user_id, item_id=item_id)
    db.add(new_cart_item)
    db.commit()
    db.refresh(new_cart_item)
    return new_cart_item

def remove_item_from_cart(db: Session, user_id: int, item_id: int):
    cart_item = (
        db.query(models.Cart).filter_by(user_id=user_id, item_id=item_id).first()
    )
    print(cart_item)
    if cart_item:
        db.delete(cart_item)
        db.commit()
        return cart_item
    return None

def get_cart_items_by_user(user_id: int, db: Session):
    return (
        db.query(models.Cart)
        .filter_by(user_id=user_id)
        .options(joinedload(models.Cart.item))
        .all()
    )


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
                           item_image = item.item_image,
                           item_owner = item.item_owner)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

def create_review(db: Session, review: pydantic_validation.ReviewCreate):
    # Convert Pydantic model to SQLAlchemy model
    db_review = models.Review(
        user_id=review.user_id,
        text=review.text,
        rating=review.rating
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


def get_reviews(db: Session):
    return db.query(models.Review).all()

def get_reviews_with_user_login(db: Session):
    results = (
        db.query(models.Review, models.User.login)
        .join(models.User, models.Review.user_id == models.User.user_id)
        .all()
    )

    reviews_with_login = [{"review": review, "user_login": user_login} for review, user_login in results]
    return reviews_with_login

def get_user_data(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()

    if user:
        user_data = {
            'user_id': user.user_id,
            'login': user.login,
            'email': user.email,
        }

        # Add more logic to fetch user items if needed

        return user_data
    return None