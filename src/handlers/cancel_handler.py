from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel and end the conversation."""
    if not update.message or not update.effective_user:
        return ConversationHandler.END

    await update.message.reply_text(
        "❌ Отмена.",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END