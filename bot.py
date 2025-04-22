import logging

from telegram.ext import Application, Updater, CallbackContext, ContextTypes, CommandHandler, MessageHandler, filters
from telegram import InputFile, User, Chat, Update
from dotenv import load_dotenv
import os

import database.settings as settings

logging.basicConfig(filename="bot.log", level=logging.INFO)

load_dotenv()

BOT_TOKEN = settings.BOT_TOKEN
# PROXY_IP = settings.PROXY_IP
# HTTP_PORT = settings.HTTP_PORT
# SOCKS5_PORT = settings.SOCKS5_PORT
# LOGIN = settings.LOGIN
# PASSWORD = settings.PASSWORD

# PROXY_URL = f"socks5://{LOGIN}:{PASSWORD}@{PROXY_IP}:{SOCKS5_PORT}"
# print(PROXY_URL)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Получена команда /start")
    await update.message.reply_text("Привет! Я бот для определения степени облысения на голове.")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Получено сообщение")
    await update.message.reply_text(update.message.text)

async def send_photo(update: Update, context):
    print("Получено изображение")
    await update.message.reply_text("Получено изображение от пользователя.")
    os.makedirs('downloads', exist_ok=True)
    photo_file = await context.bot.get_file(update.message.photo[-1].file_id)
    filename = os.path.join('downloads', f'{photo_file.file_id}.jpg')
    print(filename)
    await photo_file.download_to_drive(filename)
    await update.message.reply_text(f'Файл сохранен как {filename}')

def main():
    application = (
        Application.builder().token(BOT_TOKEN).build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT, echo))
    application.add_handler(MessageHandler(filters.PHOTO, send_photo))

    application.run_polling()


if __name__ == "__main__":
    main()