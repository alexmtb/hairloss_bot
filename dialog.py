from telegram import ReplyKeyboardRemove, Update
from telegram.ext import Updater, MessageHandler, filters, ConversationHandler


async def start_dialog(update: Update, context):
    await update.message.reply_text(
        'Как Вас зовут? Напишите свое имя.',
        reply_markup=ReplyKeyboardRemove()
    )

    return 'name'