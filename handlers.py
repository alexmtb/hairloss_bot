import os
import logging
from telegram.ext import (Application, CallbackContext, ContextTypes,
                          CommandHandler, MessageHandler, ConversationHandler, filters)
from telegram import InputFile, User, Chat, Update, ReplyKeyboardMarkup
from database.session import db_session
from database.crud import get_or_create_user, create_observation
from database.models import Observations
from utils import main_menu_keyboard, norwood_keyboard, photo_keyboard, map_class_to_descr
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io

logging.basicConfig(filename="bot.log", level=logging.INFO)

# Model constants
IMAGE_SIZE = 224
NUM_CLASSES = 7
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load model
model_path = 'model/model_weights.pth'
model = models.mobilenet_v2(weights=None)
num_filters = model.last_channel
model.classifier = nn.Sequential(
    nn.Dropout(0.2),
    nn.Linear(num_filters, NUM_CLASSES)
)
model.load_state_dict(torch.load(model_path, map_location=DEVICE))
model = model.to(DEVICE)
model.eval()

PHOTO_PREDICTION = 1

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return
    print("Получена команда /start")
    logging.info("Получена команда /start")
    user = get_or_create_user(db_session(), update.effective_user, update.message.chat_id)
    await update.message.reply_text(
        f"""Привет {update.effective_user.first_name}! Я бот для определения степени облысения на голове по шкале Гамильтона-Норвуда.\
        \nВыбери действие:""",
        reply_markup=main_menu_keyboard
    )

async def about_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot description"""
    if not update.message:
        return
    await update.message.reply_text(
        'Этот бот использует шкалу Гамильтона-Норвуда для оценки степени облысения.\
        Просто отправь фото головы сверху — и я определю стадию.')

async def norwood_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    text = (
        "📊 *Шкала Гамильтона–Норвуда* — это классификация мужского облысения. Она включает 7 стадий:\n\n"
        "1️⃣ Нет видимого облысения, нормальная линия роста волос\n"
        "2️⃣ Небольшой отступ линии волос в височной области, M-образная форма волосяного покрова\n"
        "3️⃣ Глубокий отступ линии волос в височной и лобной областях. \
            Возможна потеря волос на макушке. Начало облысения\n"
        "4️⃣ Более выраженное облысение с небольшой полосой волос между передней и задней лысиной\n"
        "5️⃣ Более крупные залысины с узкой полосой редких волос, разделяющей их\n"
        "6️⃣ Залысины на макушке и спереди соединились, полоса волос между ними отсутствует\n"
        "7️⃣ Наиболее продвинутая форма облысения, остались только волосы по бокам и сзади головы\n\n"
        "Выбери, что делать дальше:"
    )
    await update.message.reply_text(text, reply_markup=norwood_keyboard, parse_mode='HTML')


async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Returning to main menu"""
    if not update.message:
        return
    await update.message.reply_text(
        "🏠 Главное меню. Выбери действие:",
        reply_markup=main_menu_keyboard
    )

async def request_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Request photo from user"""
    if not update.message:
        return
    await update.message.reply_text(
        "Пожалуйста, отправьте фотографию волос для анализа.",
        reply_markup=photo_keyboard
    )
    return PHOTO_PREDICTION

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle received photo"""
    if not update.message:
        return
    if not update.message or not update.message.photo:
        await update.message.reply_text(
            "Пожалуйста, отправьте фотографию.",
            reply_markup=photo_keyboard
        )
        return PHOTO_PREDICTION
    
    try:
        # Создаем единую сессию для всех операций с БД
        db = db_session()
        
        # Получаем информацию о пользователе
        user = get_or_create_user(db, update.effective_user, update.message.chat_id)
        
        # Получаем фотографию
        photo_file = await context.bot.get_file(update.message.photo[-1].file_id)
        usr_photo = await photo_file.download_as_bytearray()
        
        # Convert photo to PIL Image
        image = Image.open(io.BytesIO(usr_photo)).convert('RGB')
        
        # Preprocess image
        resized_img = transforms.Resize((IMAGE_SIZE, IMAGE_SIZE))(image)
        tensor = transforms.ToTensor()(resized_img)
        norm_tensor = transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])(tensor)
        batch = norm_tensor.unsqueeze(0).to(DEVICE)

        # Model prediction
        with torch.no_grad():
            outputs = model(batch)
            probs = torch.softmax(outputs, dim=1)
            _, pred_class = torch.max(outputs, 1)
            
        # Get prediction and description
        stage = pred_class.item() + 1  # Convert to 1-based indexing
        description = await map_class_to_descr(int(pred_class.item()))
        
        # # Сохраняем результат в базу данных
        # create_observation(
        #     db=db, 
        #     tg_id=user.tg_id, 
        #     photo=photo_file.file_id,  # Храним ID фотографии из Telegram
        #     model_result=f"Стадия {stage}"
        # )
        
        await update.message.reply_text(
            f"Предполагаемая стадия: {stage}\n{description}",
            reply_markup=photo_keyboard
        )
        return ConversationHandler.END

    except Exception as e:
        print(f"Error in handle_photo: {e}")
        await update.message.reply_text(
            "Произошла ошибка при обработке фотографии.",
            reply_markup=photo_keyboard
        )
        return ConversationHandler.END

async def cancel_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel photo prediction"""
    if not update.message:
        return
    await update.message.reply_text(
        "Операция отменена.",
        reply_markup=main_menu_keyboard
    )
    return ConversationHandler.END