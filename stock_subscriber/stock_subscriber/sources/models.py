from sqlalchemy import (Column, Integer, String, ForeignKey, UniqueConstraint, Float, DateTime, Enum)
from stock_subscriber.sources.database import Base


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
    type = Column(Enum('cross', 'drop'), nullable=True)
    value = Column(Float, nullable=False)
    expire = Column(DateTime, nullable=False)

    __table_args__ = (UniqueConstraint('stock_id', 'type', 'value'),)
