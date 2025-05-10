from telegram import ReplyKeyboardRemove, Update
from telegram.ext import Updater, MessageHandler, filters, ConversationHandler
from utils import main_menu_keyboard
from database.session import db_session
from database.crud import get_or_create_user


async def start_dialog(update: Update, context):
    if not update.message or not update.effective_user:
        return ConversationHandler.END
    
    user = get_or_create_user(db_session(), update.effective_user, update.message.chat_id)
    await update.message.reply_text(
        f'Привет, {update.effective_user.first_name}!\
        Я бот для определения степени облысения на голове по шкале Гамильтона-Норвуда.\
        \nВыбери действие:',
        reply_markup=main_menu_keyboard
    )

    return 'name'