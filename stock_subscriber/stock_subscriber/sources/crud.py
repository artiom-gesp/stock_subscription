from typing import List
from stock_subscriber.sources.models import Stock, Subscription, User, Note, Category
from stock_subscriber.sources.schemas import StockIn, SubscriptionIn, UserInDB, NoteIn, CategoryIn, NoteUpdate

def create_stock(db, stock_in: StockIn):
    stock = Stock(
                ticker_symbol=stock_in.ticker_symbol,
                full_name=stock_in.full_name,
                last_price=stock_in.last_price,
                last_fetch_date=stock_in.last_fetch_date
            )
    db.add(stock)
    db.commit()
    db.refresh(stock)
    return stock

def create_subscription(db, subscription_in: SubscriptionIn):
    subscription = Subscription(
                                stock_id=subscription_in.stock_id,
                                type=subscription_in.type,
                                value=subscription_in.value,
                                expire=subscription_in.expire
                    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription

def get_stock(db, **kwargs):
    return db.query(Stock).filter_by(**kwargs).first()

def get_stocks(db, **kwargs):
    return db.query(Stock).filter_by(**kwargs).all()

def get_subscription(db, **kwargs):
    return db.query(Subscription).filter_by(**kwargs).first()

def get_subscriptions(db, **kwargs):
    return db.query(Subscription).filter_by(**kwargs).all()

def get_stocks_by_subscription(db):
    return db.query(Subscription, Stock).join(Stock).all()

def update_stock(db, db_obj, stock_in: StockIn):
    obj_in = stock_in.dict(exclude_unset=True)
    for key, value in obj_in.items():
        if hasattr(db_obj, key):
            setattr(db_obj, key, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_subscription(db, id):
    obj = db.query(Subscription).filter(id == id).first()
    if obj is not None:
        db.delete(obj)
        db.commit()

def get_user(db, **kwargs):
    return db.query(User).filter_by(**kwargs).first()

def create_user(db, user_in: UserInDB):
    user = User(
                username=user_in.username,
                hashed_password=user_in.hashed_password
            )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_note(db, **kwargs):
    return db.query(Note).filter_by(**kwargs).first()

def get_notes(db, **kwargs):
    return db.query(Note).filter_by(**kwargs).all()

def create_note(db, note_in: NoteIn):
    categories = db.query(Category).filter(Category.id.in_(note_in.categories))
    note = Note(
                title=note_in.title,
                date=note_in.date,
                content=note_in.content,
                user_id=note_in.user_id,
            )
    db.add(note)
    db.commit()
    db.refresh(note)
    note.categories = note_in.categories
    return note

def get_category(db, **kwargs):
    return db.query(Category).filter_by(**kwargs).first()

def get_categories(db, **kwargs):
    return db.query(Category).filter_by(**kwargs).all()

def create_category(db, category_in: CategoryIn):
    category = Category(
                name=category_in.name,
            )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

def delete_note(db, note_id):
    obj = db.query(Note).filter(id == id).first()
    if obj is not None:
        db.delete(obj)
        db.commit()

def update_note(db, db_obj, note_in: NoteUpdate):
    obj_in = note_in.dict(exclude_unset=True)
    for key, value in obj_in.items():
        if hasattr(db_obj, key):
            setattr(db_obj, key, value)
    db.add(db_obj)
    db_obj.categories = note_in.categories
    db.commit()
    db.refresh(db_obj)
    return db_obj