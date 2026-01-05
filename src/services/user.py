from services.base import BaseService
from datetime import datetime, timezone
import telegram
from sqlmodel import select
from loguru import logger

from database.models import User

class UserService(BaseService):
    def __init__(self):
        super().__init__()

    def add_or_update_user(self, telegram_user: telegram.User):
        query = select(User).where(User.telegram_id == telegram_user.id)
        result = self.session.exec(query)
        user = result.first()

        if not user:
            user = User(
                telegram_id = telegram_user.id,
                first_name = telegram_user.first_name,
                last_name = telegram_user.last_name,
                username = telegram_user.username
            )
            self.session.add(user)
            self.session.commit()
            logger.info(f"User {telegram_user.id} ({telegram_user.username}) inserted")
        self.update(telegram_user.id)

    def update(self, id: int):
        user = self.session.exec(select(User).where(User.telegram_id == id)).one()
        user.last_interaction = datetime.now(timezone.utc)
        self.session.add(user)
        self.session.commit()