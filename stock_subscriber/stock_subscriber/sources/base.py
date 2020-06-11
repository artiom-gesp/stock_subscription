from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import stock_subscriber.config.conf as settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, pool_recycle=2000, pool_size=10)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
