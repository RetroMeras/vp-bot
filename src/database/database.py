from sqlmodel import SQLModel, Session, create_engine
from config import settings
from database import models as _
from loguru import logger

engine = create_engine(
    url=settings.database,
    future=True
)

def init_db():
    SQLModel.metadata.create_all(engine)
    logger.info("Database initialized")

def get_session() -> Session:
    return Session(engine)