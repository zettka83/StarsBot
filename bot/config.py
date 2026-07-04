import os
from dotenv import load_dotenv
from pathlib import Path

# Вычисляем точный путь к файлу .env в папке bot
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

# Принудительно читаем именно этот файл
load_dotenv(ENV_PATH)

# Забираем переменные по их ИМЕНАМ
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Проверка, чтобы терминал сразу сказал, в чём дело
if not BOT_TOKEN:
    print(f"❌ ОШИБКА: Токен не найден! Скрипт искал его здесь: {ENV_PATH}")
    print("Убедитесь, что внутри файла написано: BOT_TOKEN=ваш_токен")
    exit()

# Остальные переменные
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
CHANNELS_STR = os.getenv("CHANNELS", "")
CHANNELS = [ch.strip() for ch in CHANNELS_STR.split(",") if ch.strip()]