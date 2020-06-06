from stock_subscriber.sources.database import SessionLocal, init_db
from stock_subscriber.sources.api.api import router
from fastapi import FastAPI
import argparse

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    session = SessionLocal()
    init_db(session)


@app.get("/")
def root():
    return {"message": "Hello World"}


app.include_router(router)
