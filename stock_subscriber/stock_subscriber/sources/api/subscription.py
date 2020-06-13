from fastapi import APIRouter, Depends, HTTPException, status
from stock_subscriber.sources.schemas import StockIn, SubscriptionIn, User
from stock_subscriber.sources.utils import get_db
from sqlalchemy.orm import Session
from stock_subscriber.sources import crud
from stock_subscriber.sources.subscription import subscribe, check_subscriptions
from stock_subscriber.sources.account_utils import get_current_user

router = APIRouter()

@router.post("/subscription")
def create_subcription(
    subscription_in: SubscriptionIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = subscribe(db, subscription_in=subscription_in)
    return success


@router.get("/check")
def check_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_subscriptions(db)


@router.get("/stock")
def get_stocks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_stocks(db)


@router.get("/stock/{stock_id}")
def get_stock(
    stock_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_stock(db, id=stock_id, user_id=current_user.id)


@router.get("/stock/{stock_id}/subscriptions")
def get_subscriptions(
    stock_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    stock = crud.get_stock(db, id=stock_id)
    if not stock:
        return HTTPException(status.HTTP_404_NOT_FOUND)
    return crud.get_subscriptions(db, stock_id=stock_id)