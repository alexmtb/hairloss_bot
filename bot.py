import logging
import os

from telegram.ext import (Application, Updater, CallbackContext, ContextTypes,
                          CommandHandler, MessageHandler, ConversationHandler, filters)
from telegram import InputFile, User, Chat, Update, ReplyKeyboardMarkup
import database.settings as settings
from handlers import start, echo, send_photo
from dialog import start_dialog

logging.basicConfig(filename="bot.log", level=logging.INFO)

BOT_TOKEN = settings.BOT_TOKEN


def main():
    application = (
        Application.builder().token(BOT_TOKEN).build()
    )
    dialog = ConversationHandler(
        entry_points = [
            MessageHandler(filters.Regex('^(Начать работу)$'), start_dialog)
        ],
        states = {
            'name': [MessageHandler(filters.TEXT, lambda update, context: None)]
        },
        fallbacks = []
    )
    application.add_handler(dialog)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT, echo))
    application.add_handler(MessageHandler(filters.PHOTO, send_photo))

    logging.info('Bot has been started.')
    application.run_polling()


if __name__ == "__main__":
    main()