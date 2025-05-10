import logging
import os

from telegram.ext import (Application, Updater, CallbackContext, ContextTypes,
                          CommandHandler, MessageHandler, ConversationHandler, filters)
from telegram import InputFile, User, Chat, Update, ReplyKeyboardMarkup
import database.settings as settings
from handlers import (start_handler, about_bot, norwood_info, back_to_main_menu,
                     request_photo, handle_photo, cancel_photo, PHOTO_PREDICTION)
from dialog import start_dialog

logging.basicConfig(filename="bot.log", level=logging.INFO)

BOT_TOKEN = settings.BOT_TOKEN

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END

def main():
    app = (
        Application.builder().token(BOT_TOKEN).build()
    )
    
    # Photo prediction conversation
    photo_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Text(
            ['📸 Отправить фото', '📤 Отправить другое фото']
        ), request_photo)],
        states={
            PHOTO_PREDICTION: [
                MessageHandler(filters.PHOTO, handle_photo),
                MessageHandler(filters.Text(['🏠 Главное меню']), cancel_photo)
            ]
        },
        fallbacks=[MessageHandler(filters.ALL, cancel_photo)],
        conversation_timeout=20
    )
    
    # Name dialog
    name_dialog = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^(👤 Начать)$'), start_dialog)],
        states={
            'name': [MessageHandler(filters.TEXT, handle_name)]
        },
        fallbacks=[]
    )
    
    app.add_handler(name_dialog)
    app.add_handler(photo_conv)
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(MessageHandler(filters.Text(['👤 Начать']), start_handler))
    app.add_handler(MessageHandler(filters.Text(['ℹ️ О боте']), about_bot))
    app.add_handler(MessageHandler(filters.Text(['📊 Шкала Норвуда']), norwood_info))
    app.add_handler(MessageHandler(filters.Text(['🏠 Главное меню', 'Меню']), back_to_main_menu))

    logging.info('Bot has been started.')
    app.run_polling()


if __name__ == "__main__":
    main()