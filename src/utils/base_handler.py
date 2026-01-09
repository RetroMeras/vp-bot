from typing import Optional
from telegram import Update, Message

class BaseHandler:
    """Provides common utilities for all handlers"""

    @staticmethod
    async def get_effective_message(update: Update) -> Optional[Message]:
        """Get message from update (handles both message and callback_query)"""
        if update.message:
            return update.message
        elif update.callback_query and update.callback_query.message:
            return update.callback_query.message # ty: ignore[invalid-return-type]
        return None

    @staticmethod
    async def safe_edit_or_reply(update: Update, text: str, **kwargs) -> None:
        """Safely reply, handling both message and callback_query"""
        if update.callback_query:
            await update.callback_query.edit_message_text(text=text, **kwargs)
        elif update.message:
            await update.message.reply_text(text=text, **kwargs)

    @staticmethod
    def get_user_id(update: Update) -> Optional[int]:
        """Extract user ID from update"""
        return update.effective_user.id if update.effective_user else None