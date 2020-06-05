import argparse
import yfinance as yf
import datetime
import mysql.connector
import requests


SMS_LOGIN = {
    'user': 14018314,
    'pass': 'BCDE7PlmW4F2Tj'
}

TABLES = {
    "stocks": ("CREATE TABLE `stocks` ("
               "`id` INT NOT NULL AUTO_INCREMENT, "
               "`ticker_symbol` CHAR(7) NOT NULL UNIQUE, "
               "`full_name` CHAR(7), "
               "`last_price` FLOAT, "
               "`last_fetch_date` date, "
               "PRIMARY KEY (id)) "
               "ENGINE=InnoDB"),
    "subscriptions": ("CREATE TABLE `subscriptions` ("
                      "`id` INT NOT NULL AUTO_INCREMENT, "
                      "stock_id int NOT NULL,"
                      "`type` ENUM('cross', 'drop'), "
                      "`value` FLOAT, "
                      "`expire` date, "
                      "FOREIGN KEY (stock_id) REFERENCES stocks(id), "
                      "PRIMARY KEY (id), "
                      "UNIQUE(stock_id, type, value)) "
                      "ENGINE=InnoDB")
}

add_stock = ("INSERT INTO stocks "
               "(ticker_symbol, full_name, last_price, last_fetch_date) "
               "VALUES (%s, %s, %s, %s)")

add_subscription = ("INSERT INTO subscriptions "
               "(stock_id, type, value, expire) "
               "VALUES (%s, %s, %s, %s)")


def checkTableExists(mydb, tablename):
    cursor = mydb.cursor()
    cursor.execute("""
      SELECT COUNT(*)
      FROM information_schema.tables
      WHERE table_name = '{0}'
      """.format(tablename.replace('\'', '\'\'')))
    if cursor.fetchone()[0] == 1:
        cursor.close()
        return True

    cursor.close()
    return False


def createIfNotExists(mydb):
    for tablename in TABLES.keys():
        if not checkTableExists(mydb, tablename):
            cursor = mydb.cursor()
            print(TABLES[tablename])
            cursor.execute(TABLES[tablename])
            cursor.close()


def has_crossed(current_price, last_price, cross_value):
    return last_price < cross_value < current_price or current_price < cross_value < last_price


def send_cross_message(ticker_symbol, current_price, cross_value):
    msg = f'{ticker_symbol} crossed the set threshold ({cross_value}) and is now selling at {current_price}.'
    params = {
        'user': SMS_LOGIN['user'],
        'pass': SMS_LOGIN['pass'],
        'msg': msg
    }
    requests.get('https://smsapi.free-mobile.fr/sendmsg', params=params)


def check_subscriptions(mydb):
    cursor = mydb.cursor()
    cursor.execute("SELECT stocks.ticker_symbol, stocks.last_price, subscriptions.type, subscriptions.value, "
                   "subscriptions.id "
                   "FROM `subscriptions` INNER JOIN `stocks` on stocks.id=subscriptions.stock_id")
    stocks = cursor.fetchall()
    cursor.close()
    for stock in stocks:
        data = yf.download(stock[0], period="1d", interval="1m")[-3:]
        current_price = round(data['Adj Close'].sum() / 3, 3)
        if stock[2] == 'cross' and has_crossed(current_price, stock[1], stock[3]):
            print("HAS_CROSSED")
            send_cross_message(stock[0], current_price, stock[3])
            cursor = mydb.cursor()
            print(stock[4])
            cursor.execute(f"DELETE FROM `subscriptions` WHERE id='{stock[4]}'")
            mydb.commit()
            cursor.close()

        # print(f'current {current_price} \n{data.to_string()[:-3]}\n')
        cursor = mydb.cursor()
        cursor.execute(f"UPDATE `stocks` "
                       f"SET last_price='{current_price}' "
                       f"WHERE ticker_symbol='{stock[0]}'")
        # mydb.commit()
        cursor.close()


def stock_exists(mydb, ticker_symbol):
    cursor = mydb.cursor()
    cursor.execute(f"SELECT id FROM `stocks` WHERE ticker_symbol='{ticker_symbol}'")
    id = cursor.fetchone()
    cursor.close()
    return id[0] if id else None


def get_or_create_stock(mydb, ticker_symbol, last_price):
    stock_id = stock_exists(mydb, ticker_symbol)
    if not stock_id:
        cursor = mydb.cursor()
        cursor.execute(add_stock, (ticker_symbol, None, last_price, datetime.datetime.now().isoformat()))
        mydb.commit()
        cursor.close()
        stock_id = stock_exists(mydb, ticker_symbol)
    return stock_id


def build_expire_date(days):
    return datetime.datetime.now() + datetime.timedelta(days=days)


def value_type_valid(type, value):
    if type == 'cross':
        return value > 0
    if type == 'drop':
        return 0 < value < 100


def subscribe(mydb, ticker_symbol, type, value, expire=None):
    print(ticker_symbol)
    data = yf.download(ticker_symbol, period="1d", interval="1m")[-3:]
    if data.empty:
        return False
    if not value_type_valid(type, value):
        return False

    last_price = round(data['Adj Close'].sum() / 3, 3)
    stock_id = get_or_create_stock(mydb, ticker_symbol, last_price)
    expire = expire if expire else 5
    expire = build_expire_date(expire)

    try:
        cursor = mydb.cursor()
        cursor.execute(add_subscription, (stock_id, type, value, expire))
        mydb.commit()
        cursor.close()
        return True
    except mysql.connector.errors.DatabaseError as e:
        print(e)
        return False


# createIfNotExists(mydb)

# print(f"val {subscribe(mydb, 'AAPL', 'cross', 305.20, expire=12)}")
# check_subscriptions(mydb)

if __name__ == '__main__':
    mydb = mysql.connector.connect(
        host="localhost",
        user="trading_notifications",
        passwd="@12pm1G0T0Sl33p",
        database="trading_notifications"
    )
    createIfNotExists(mydb)

    parser = argparse.ArgumentParser()
    parser.add_argument("action", type=str, choices=['check', 'subscribe'], help="Action to perform")
    parser.add_argument("--ticker_symbol", help="Subscription ticker symbol")
    parser.add_argument("--type", type=str, choices=['cross', 'drop'], help="Subscription type")
    parser.add_argument("--value", type=float,
                        help="Subscription value to be crossed for [cross] or percentage for [drop]")
    parser.add_argument("--expire", type=int, help="Subscription expiry date")

    args = parser.parse_args()

    if args.action == 'subscribe' and not(args.ticker_symbol or args.type or args.value):
        print('You need to specify ticker_symbol, type and value')
    elif args.action == 'subscribe':
        success = subscribe(mydb, args.ticker_symbol, args.type, args.value, args.expire)
        print('Success') if success else print('Failure')
    else:
        check_subscriptions(mydb)
