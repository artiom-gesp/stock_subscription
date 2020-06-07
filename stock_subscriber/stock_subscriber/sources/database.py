from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import stock_subscriber.config.conf as settings
from stock_subscriber.sources import crud
from stock_subscriber.sources.schemas import UserInDB
from stock_subscriber.sources.account_utils import pwd_context
from stock_subscriber.sources.base import Base, engine



def init_db(db: Session) -> None:  # pylint: disable=invalid-name
    Base.metadata.create_all(bind=engine)
    admin = UserInDB(username=settings.ADMIN_USERNAME, hashed_password=pwd_context.hash(settings.ADMIN_PASSWORD))
    crud.create_user(db, user_in=admin)