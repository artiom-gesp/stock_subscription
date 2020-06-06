from stock_subscriber.sources.database import SessionLocal, init_db
from stock_subscriber.sources.api.api import router
from fastapi import APIRouter, Depends, HTTPException, status
from stock_subscriber.sources.subscription import check_subscriptions
from fastapi_utils.tasks import repeat_every
from fastapi import FastAPI
import argparse

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    init_db(db)

@app.on_event("startup")
@repeat_every(seconds=240) 
async def get_periodical_subscriptions() -> None:
    db = SessionLocal()
    check_subscriptions(db)



@app.get("/")
def root():
    return {"message": "Hello World"}


app.include_router(router)
