from sqlalchemy import (Column, Integer, String, ForeignKey, UniqueConstraint, Float, DateTime, Enum, Text)
from stock_subscriber.sources.base import Base
from sqlalchemy.orm import relationship


class Stock(Base):
    __tablename__ = 'stock'

    id = Column(Integer, primary_key=True)
    ticker_symbol = Column(String(8), nullable=False, unique=True)
    full_name = Column(String(16), nullable=True)
    last_price = Column(Float, nullable=False)
    last_fetch_date = Column(DateTime, nullable=False)

class Subscription(Base):
    __tablename__ = 'subscription'

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey(Stock.id, ondelete='CASCADE'), nullable=False)
    type = Column(Enum('cross', 'drop'), nullable=False)
    value = Column(Float, nullable=False)
    expire = Column(DateTime, nullable=False)

    __table_args__ = (UniqueConstraint('stock_id', 'type', 'value'),)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(16), nullable=True)
    hashed_password = Column(String(72), nullable=True)

class Category(Base):
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=True)

class Note(Base):
    __tablename__ = 'note'

    id = Column(Integer, primary_key=True)
    title = Column(String(32), nullable=True)
    user_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), nullable=False)
    date = Column(DateTime, nullable=False)
    content = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey(Category.id, ondelete='SET NULL'))
    categories = relationship("Category", uselist=True)

