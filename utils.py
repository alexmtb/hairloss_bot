from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from dialog import start_dialog


async def main_keyboard():
    await ReplyKeyboardMarkup(
        [
            ['Начать работу']
        ]
    )






    # inline_keyboard = [
    #     [
    #         InlineKeyboardButton('Познакомиться', callback_data='1'),
    #         InlineKeyboardButton('Отправить фото', callback_data='2')
    #     ]
    # ]

    # return InlineKeyboardMarkup(inline_keyboard)