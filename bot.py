import logging

from telegram.ext import Application, Updater, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import os

import settings

logging.basicConfig(filename="bot.log", level=logging.INFO)

load_dotenv()

BOT_TOKEN = settings.BOT_TOKEN
PROXY_IP = settings.PROXY_IP
HTTP_PORT = settings.HTTP_PORT
SOCKS5_PORT = settings.SOCKS5_PORT
LOGIN = settings.LOGIN
PASSWORD = settings.PASSWORD


PROXY_URL = f"socks5://{LOGIN}:{PASSWORD}@{PROXY_IP}:{SOCKS5_PORT}"
print(PROXY_URL)

async def start(update, context):
    print("Получена команда /start")
    await update.message.reply_text("Привет! Я бот")

application = Application.builder() \
    .token(BOT_TOKEN) \
    .build()


application.add_handler(CommandHandler("start", start))
# application.add_handler(MessageHandler(filters.TEXT, echo))

application.run_polling()