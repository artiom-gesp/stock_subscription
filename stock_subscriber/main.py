from stock_subscriber.sources.database import init_db
from stock_subscriber.sources.base import SessionLocal
from stock_subscriber.sources.api.subscription import router as sub_router 
from stock_subscriber.sources.api.account import router as acc_router
from stock_subscriber.sources.api.note import router as note_router
from fastapi import APIRouter, Depends, HTTPException, status
from stock_subscriber.sources.subscription import check_subscriptions
from fastapi_utils.tasks import repeat_every
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import argparse
import logging
from fastapi.logger import logger as fastapi_logger


gunicorn_error_logger = logging.getLogger("gunicorn.error")
gunicorn_logger = logging.getLogger("gunicorn")
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.handlers = gunicorn_error_logger.handlers

fastapi_logger.handlers = gunicorn_error_logger.handlers

fastapi_logger.setLevel(gunicorn_logger.level)

app = FastAPI()

origins = [
    "*",
]


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


app.include_router(sub_router)
app.include_router(acc_router)
app.include_router(note_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)