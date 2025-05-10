from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        ["👤 Начать", "ℹ️ О боте"],
        ["📊 Шкала Норвуда", "📸 Отправить фото"],
        ["🕓 История распознаваний"]
    ],
    resize_keyboard=True
)

norwood_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        ["🖼 Показать примеры"],
        ["🏠 Главное меню"]
    ],
    resize_keyboard=True
)

photo_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        ["📤 Отправить другое фото"],
        ["🏠 Главное меню"]
    ],
    resize_keyboard=True
)

async def map_class_to_descr(class_idx: int) -> str:
    """Maps class index to Norwood stage description in Russian"""
    descriptions = [
        "Стадия 1: Нет видимого облысения, нормальная линия роста волос",
        "Стадия 2: Небольшой отступ линии волос в височной области, M-образная форма", 
        "Стадия 3: Глубокий отступ линии волос в височной и лобной областях",
        "Стадия 4: Более выраженное облысение с небольшой полосой волос между передней и задней лысиной",
        "Стадия 5: Более крупные залысины с узкой полосой редких волос, разделяющей их",
        "Стадия 6: Залысины на макушке и спереди соединились, полоса волос между ними отсутствует",
        "Стадия 7: Наиболее тяжелая форма облысения, остались только волосы по бокам и сзади головы"
    ]
    return descriptions[class_idx]