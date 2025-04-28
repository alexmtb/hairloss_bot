import os
import logging
from telegram.ext import Application, CallbackContext, ContextTypes, CommandHandler, MessageHandler, filters
from telegram import InputFile, User, Chat, Update, ReplyKeyboardMarkup
from database.session import db_session
from database.crud import create_observation
from database.models import Observations

logging.basicConfig(filename="bot.log", level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_keyboard = ReplyKeyboardMarkup([['/start']])
    print("Получена команда /start")
    logging.info("Получена команда /start")
    await update.message.reply_text(
        "Привет! Я бот для определения степени облысения на голове по шкале Гамильтона-Норвуда.",
        reply_markup=start_keyboard
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Получено сообщение")
    await update.message.reply_text(update.message.text)

# async def check_user(update: Update, ):


async def send_photo(update: Update, context):
    print("Получено изображение")
    await update.message.reply_text("Получено изображение от пользователя.")
    os.makedirs('downloads', exist_ok=True)
    photo_file = await context.bot.get_file(update.message.photo[-1].file_id)
    filename = os.path.join('downloads', f'{photo_file.file_id}.jpg')
    print(filename)
    await photo_file.download_to_drive(filename)
    await update.message.reply_text(f'Файл сохранен как {filename}')

    # add to base
    # user = update.effective_user
    # create_observation(
    #     db=db_session,
    #     id=u
    # )