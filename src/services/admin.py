from database.models import UserRole
from sqlmodel import select

from database.models import User
from services.base import BaseService


class AdminService(BaseService):
    def __init__(self):
        super().__init__()

    def is_admin(self, telegram_id: int) -> bool:
        user = self.session.exec(select(User).where(User.telegram_id == telegram_id)).one()
        return user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]

    def is_super_admin(self, telegram_id: int) -> bool:
        user = self.session.exec(select(User).where(User.telegram_id == telegram_id)).one()
        return user.role == UserRole.SUPER_ADMIN

    def change_role(self, telegram_id: int, role: UserRole):
        user = self.session.exec(select(User).where(User.telegram_id == telegram_id)).one()
        if user.role == role:
            return

        user.role = role
        self.session.add(user)
        self.session.commit()
