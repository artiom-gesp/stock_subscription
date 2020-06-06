from stock_subscriber.sources.database import SessionLocal


def get_db():
    try:
        session = SessionLocal()
        yield session
    finally:
        session.close()