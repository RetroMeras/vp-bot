from database.database import get_session
from sqlmodel import Session

class BaseService:
    def __init__(self):
        self.session: Session = get_session()