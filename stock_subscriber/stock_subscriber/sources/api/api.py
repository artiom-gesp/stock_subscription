from fastapi import APIRouter, Depends, HTTPException, status
from stock_subscriber.sources.schemas import StockIn, SubscriptionIn
from stock_subscriber.sources.utils import get_db
from sqlalchemy.orm import Session
from stock_subscriber.sources import crud
from stock_subscriber.sources.subscription import subscribe, check_subscriptions

router = APIRouter()

@router.post("/subscription/")
def create_subcription(subscription_in: SubscriptionIn, db: Session = Depends(get_db)):
    success = subscribe(db, subscription_in=subscription_in)
    return success


@router.get("/check/")
def check_subscription(db: Session = Depends(get_db)):
    check_subscriptions(db)
