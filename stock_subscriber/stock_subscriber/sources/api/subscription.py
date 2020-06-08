from fastapi import APIRouter, Depends, HTTPException, status
from stock_subscriber.sources.schemas import StockIn, SubscriptionIn, User
from stock_subscriber.sources.utils import get_db
from sqlalchemy.orm import Session
from stock_subscriber.sources import crud
from stock_subscriber.sources.subscription import subscribe, check_subscriptions
from stock_subscriber.sources.account_utils import get_current_user

router = APIRouter()

@router.post("/subscription/")
def create_subcription(
    subscription_in: SubscriptionIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = subscribe(db, subscription_in=subscription_in)
    return success


@router.get("/check/")
def check_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_subscriptions(db)
