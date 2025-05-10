import logging
import os
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import io
import matplotlib.pyplot as plt
import numpy as np
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pathlib import Path
import database.settings as settings
from database.session import get_session
from database.models import User, Observations

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Параметры модели
NUM_CLASSES = 7
IMAGE_SIZE = 224
MODEL_PATH = 'model/mobilenet_hairloss_model.pth'

# Устройство для вычислений
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(f"Используемое устройство: {device}")

# Преобразование для входного изображения
transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Описания классов
class_descriptions = [
    "Стадия 1: Нет видимого облысения, нормальная линия роста волос",
    "Стадия 2: Небольшой отступ линии волос в височной области, M-образная форма",
    "Стадия 3: Глубокий отступ линии волос в височной и лобной области",
    "Стадия 4: Более выраженное облысение с небольшой полосой волос между передней и задней лысиной",
    "Стадия 5: Более крупные залысины с узкой полосой редких волос, разделяющей их",
    "Стадия 6: Залысины на макушке и спереди соединились, полоса волос между ними отсутствует",
    "Стадия 7: Наиболее тяжелая форма облысения, остались только волосы по бокам и сзади головы"
]

# Загрузка модели
def load_model(model_path):
    """
    Загрузка предварительно обученной модели MobileNetV2
    """
    # Инициализация модели
    model = models.mobilenet_v2(weights=None)
    
    # Модифицируем последний слой для нашей задачи классификации
    num_ftrs = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(num_ftrs, NUM_CLASSES)
    
    # Загрузка весов, если файл существует
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path, map_location=device))
        print(f"Модель успешно загружена из {model_path}")
    else:
        print(f"Файл модели не найден: {model_path}")
        print("Используется неинициализированная модель")
    
    model = model.to(device)
    model.eval()  # Переключаем в режим оценки
    
    return model

# Предсказание на изображении
def predict_image(model, image):
    """
    Предсказание класса для изображения
    """
    # Преобразование изображения в тензор
    image_tensor = transform(image).unsqueeze(0).to(device)
    
    # Делаем предсказание
    with torch.no_grad():
        outputs = model(image_tensor)
        probs = torch.softmax(outputs, dim=1)
        _, pred_class = torch.max(outputs, 1)
    
    return pred_class.item(), probs.cpu().numpy()[0]

# Создание визуализации результата
def create_visualization(image, pred_class, probs):
    """
    Создание визуализации результата предсказания
    """
    # Создание фигуры для визуализации
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Отображение изображения
    ax1.imshow(image)
    ax1.set_title(f"Предсказанный класс: {pred_class+1}")
    ax1.axis('off')
    
    # Отображение вероятностей
    class_names = [f"Класс {i+1}" for i in range(NUM_CLASSES)]
    y_pos = np.arange(len(class_names))
    
    ax2.barh(y_pos, probs, align='center')
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(class_names)
    ax2.set_xlabel('Вероятность')
    ax2.set_title('Вероятности по классам')
    
    plt.tight_layout()
    
    # Сохранение изображения в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    
    return buf

# Загрузка модели
model = load_model(MODEL_PATH)

# Обработчики команд Telegram бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Создание или получение пользователя в БД
    with get_session() as session:
        db_user = User(
            tg_id=user.id,
            username=user.username,
            first_name=user.first_name
        )
        session.add(db_user)
        session.commit()
    
    await update.message.reply_text(
        f"Привет, {user.first_name}! Я бот для определения степени облысения по шкале Норвуда-Гамильтона.\n\n"
        "Отправь мне фотографию головы (желательно сверху или спереди), и я определю степень облысения."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = (
        "Я могу определить степень облысения по шкале Норвуда-Гамильтона.\n\n"
        "Как пользоваться ботом:\n"
        "1. Отправь мне фотографию головы (желательно сверху или спереди)\n"
        "2. Я проанализирую изображение и определю степень облысения\n"
        "3. Получи результат с описанием и визуализацией\n\n"
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать эту справку\n"
        "/about - Информация о боте и шкале Норвуда-Гамильтона"
    )
    await update.message.reply_text(help_text)

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /about"""
    about_text = (
        "О шкале Норвуда-Гамильтона:\n\n"
        "Шкала Норвуда-Гамильтона - это классификация степени андрогенной алопеции (мужского облысения) "
        "у мужчин, разработанная доктором О'Тара Норвудом и доктором Джеймсом Гамильтоном.\n\n"
        "Классификация включает 7 стадий облысения:\n"
    )
    
    # Добавляем описания всех стадий
    for i, desc in enumerate(class_descriptions):
        about_text += f"\n• {desc}"
    
    about_text += (
        "\n\nДанный бот использует глубокое обучение (MobileNetV2) "
        "для классификации изображений и определения стадии облысения."
    )
    
    await update.message.reply_text(about_text)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик входящих фотографий"""
    user = update.effective_user
    
    # Сообщаем пользователю, что обрабатываем фото
    await update.message.reply_text("Обрабатываю фотографию, это займет несколько секунд...")
    
    # Получаем фотографию высшего качества
    photo_file = await context.bot.get_file(update.message.photo[-1].file_id)
    photo_bytes = await photo_file.download_as_bytearray()
    
    # Сохраняем URL фотографии для записи в БД
    photo_url = photo_file.file_path
    
    # Преобразуем фото в изображение PIL
    image = Image.open(io.BytesIO(photo_bytes)).convert('RGB')
    
    try:
        # Делаем предсказание
        pred_class, probs = predict_image(model, image)
        
        # Получаем описание класса
        result_text = f"Результат анализа:\n\n{class_descriptions[pred_class]}\n\n"
        result_text += "Вероятности по классам:\n"
        
        # Добавляем вероятности для каждого класса
        for i, prob in enumerate(probs):
            result_text += f"Класс {i+1}: {prob:.2f}\n"
        
        # Создаем и отправляем визуализацию
        vis_buf = create_visualization(image, pred_class, probs)
        await update.message.reply_photo(
            InputFile(vis_buf, filename="result.png"),
            caption=result_text
        )
        
        # Сохраняем результат в БД
        with get_session() as session:
            observation = Observations(
                tg_id=user.id,
                photo_url=photo_url,
                model_result=f"Класс {pred_class+1}"
            )
            session.add(observation)
            session.commit()
        
    except Exception as e:
        logger.error(f"Ошибка при обработке изображения: {e}")
        await update.message.reply_text(
            "Произошла ошибка при обработке изображения. "
            "Пожалуйста, убедитесь, что на фотографии четко видна голова, и попробуйте еще раз."
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    await update.message.reply_text(
        "Пожалуйста, отправьте фотографию для анализа степени облысения. "
        "Для получения справки введите /help."
    )

def main():
    """Запуск бота"""
    # Получаем токен бота из настроек
    token = settings.BOT_TOKEN
    
    if not token:
        logger.error("Токен бота не найден! Пожалуйста, укажите BOT_TOKEN в файле settings.py")
        return
    
    # Создание приложения
    application = Application.builder().token(token).build()
    
    # Добавление обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Запуск бота
    logger.info("Бот запущен")
    application.run_polling()

if __name__ == "__main__":
    main() 