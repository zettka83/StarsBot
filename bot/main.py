import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import init_db
from handlers import start, tasks, admin

async def main():
    # Настройка логирования
    logging.basicConfig(level=logging.INFO)
    
    # Создаем папки
    os.makedirs("data", exist_ok=True)
    os.makedirs("images", exist_ok=True)
    
    # Инициализация БД
    await init_db()

    # Инициализация бота БЕЗ сложных кастомных сессий
    # Если интернет "глючит", попробуйте этот метод
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Подключение роутеров
    dp.include_router(start.router)
    dp.include_router(tasks.router)
    dp.include_router(admin.router)

    logging.info("Бот запущен. Ожидание обновлений...")
    
    # Запуск поллинга
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")