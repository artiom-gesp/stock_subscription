from stock_subscriber.sources.models import Stock, Subscription
from stock_subscriber.sources.schemas import StockIn, SubscriptionIn

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