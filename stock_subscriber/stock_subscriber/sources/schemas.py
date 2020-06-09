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
    expire: Optional[int] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str = None

class User(BaseModel):
    username: str

class UserInDB(User):
    hashed_password: str

class NoteIn(BaseModel):
    title: str
    user_id: Optional[int]
    date: Optional[datetime]
    content: str
    categories: List[int]

class NoteUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]
    categories: Optional[List[int]] = []

class CategoryIn(BaseModel):
    name: int