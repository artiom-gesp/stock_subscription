from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel


class StockIn(BaseModel):
    ticker_symbol: str
    full_name: Optional[str] = None
    last_price: float
    last_fetch_date: datetime

class StockUpdate(BaseModel):
    last_price: float
    last_fetch_date: datetime

class SubscriptionIn(BaseModel):
    stock_id: Optional[int] = None
    ticker_symbol: str
    type: str
    value: float
    expire: Optional[str] = None