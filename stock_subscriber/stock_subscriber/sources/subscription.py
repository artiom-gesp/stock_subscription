import argparse
import yfinance as yf
import datetime
import mysql.connector
import requests
from pytz import timezone
from stock_subscriber.sources import crud
from stock_subscriber.sources.schemas import SubscriptionIn, StockIn, StockUpdate
from stock_subscriber.config.conf import SMS_LOGIN, SMS_SERVER
from sqlalchemy.exc import IntegrityError

curr_timezone = tz=timezone('Europe/Paris')


def has_crossed(current_price, last_price, cross_value):
    print(f'la {last_price}')
    print(f'cr {cross_value}')
    print(f'cu {current_price}')
    return last_price < cross_value < current_price or current_price < cross_value < last_price


def send_cross_message(name, current_price, cross_value):
    msg = f'{name} crossed the set threshold ({cross_value}) and is now selling at {current_price}.'
    params = {
        'user': SMS_LOGIN['user'],
        'pass': SMS_LOGIN['pass'],
        'msg': msg
    }
    requests.get(SMS_SERVER, params=params)


def check_subscriptions(db):
    data = crud.get_stocks_by_subscription(db)
    for subscription, stock in data:
        name = stock.full_name if stock.full_name else stock.ticker_symbol
        print(f"Downloading data : {name} - {datetime.datetime.now(tz=curr_timezone)}")
        try:
            data = yf.download(stock.ticker_symbol, period="1d", interval="1m")[-1:]
        except Exception as e:
            print(e)
            print(f"Error fetching {stock.ticker_symbol} - {datetime.datetime.now(tz=curr_timezone)}")
            continue
        if data is None:
            print(data)
            print(f"Error fetching {stock.ticker_symbol} - {datetime.datetime.now(tz=curr_timezone)}")
            continue
        current_price = round(data['Adj Close'][0], 3)
        if subscription.type == 'cross' and has_crossed(current_price, stock.last_price, subscription.value):
            print(f"HAS_CROSSED {name} - {datetime.datetime.now(tz=curr_timezone)}")
            send_cross_message(name, current_price, subscription.value)
            crud.delete_subscription(db, id=subscription.id)                

        update = StockUpdate(last_price=current_price, last_fetch_date=datetime.datetime.now(tz=curr_timezone))
        crud.update_stock(db, stock, stock_in=update)


def build_expire_date(days):
    return datetime.datetime.now(tz=curr_timezone) + datetime.timedelta(days=days)


def value_type_valid(type, value):
    if type == 'cross':
        return value > 0
    if type == 'drop':
        return 0 < value < 100


def subscribe(db, subscription_in):
    print(subscription_in.ticker_symbol)
    ticker = yf.Ticker(subscription_in.ticker_symbol)
    data = ticker.history(period="1d", interval="1m")[-3:]
    if data.empty:
        return False
    if not value_type_valid(subscription_in.type, subscription_in.value):
        return False
    
    try:
        name = ticker.info['longName']
    except:
        name = None
    

    last_price = round(data['Close'].sum() / 3, 3)
    try:
        tz = datetime.tzinfo()
        stock_in = StockIn(ticker_symbol=subscription_in.ticker_symbol, full_name=name, last_price=last_price, last_fetch_date=datetime.datetime.now(tz=curr_timezone))
        stock = crud.create_stock(db, stock_in=stock_in)
    except IntegrityError:
        db.rollback()
        db.flush()
        stock = crud.get_stock(db, ticker_symbol=subscription_in.ticker_symbol)

    subscription_in.expire = subscription_in.expire if subscription_in.expire else 10 #days
    subscription_in.expire = build_expire_date(subscription_in.expire)

    subscription_in.stock_id = stock.id
    try:
        crud.create_subscription(db, subscription_in=subscription_in)
        return True
    except IntegrityError:
        db.rollback()
        db.flush()
        return False