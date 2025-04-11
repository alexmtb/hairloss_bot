import logging

from telegram.ext import Application, Updater, ContextTypes, CommandHandler, MessageHandler, filters
from telegram import InputFile
from dotenv import load_dotenv
import os

import settings

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

async def start(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    print("Получена команда /start")
    await update.message.reply_text("Привет! Я бот")


async def echo(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    print("Получено сообщение")
    await update.message.reply_text(update.message.text)

async def send_photo(update: Updater, context):
    print("Used command /photo")

    try:
        with open(photo_path, "rb") as photo:
            await update.message.reply_text("Here is your photo:")
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
    except FileNotFoundError:
        await update.message.reply_text("Photo wasn't found.")

application = (
    Application.builder()
    .token(BOT_TOKEN)
    .build()
)


application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT, echo))
application.add_handler(CommandHandler("photo", send_photo))

application.run_polling()