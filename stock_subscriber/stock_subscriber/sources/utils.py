from stock_subscriber.sources.base import SessionLocal
import sys, os


def get_db():
    try:
        session = SessionLocal()
        yield session
    finally:
        session.close()

def exec_without_print(func, *args, **kwargs):
    sys.stdout = open(os.devnull, 'w')
    ret = func(*args, **kwargs)
    sys.stdout = sys.__stdout__
    return ret