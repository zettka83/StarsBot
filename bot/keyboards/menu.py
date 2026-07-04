from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNELS

def get_main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Задания"), KeyboardButton(text="👤 Профиль")],
            [KeyboardButton(text="🏆 Топ пользователей"), KeyboardButton(text="ℹ️ Правила")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_subscription_menu():
    buttons = []
    for i, channel in enumerate(CHANNELS, 1):
        url = f"https://t.me/{channel.replace('@', '')}"
        buttons.append([InlineKeyboardButton(text=f"Канал партнёра №{i}", url=url)])
    
    buttons.append([InlineKeyboardButton(text="Проверить подписку", callback_data="check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_categories_menu():
    categories = ["➕ Математика", "📜 История России", "📚 Русский язык", "🧠 Логика", "🌍 География России"]
    buttons = [[KeyboardButton(text=cat)] for cat in categories]
    buttons.append([KeyboardButton(text="🔙 Назад")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_admin_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")],
            [InlineKeyboardButton(text="➕ Выдать Stars", callback_data="admin_add_stars"),
             InlineKeyboardButton(text="➖ Снять Stars", callback_data="admin_del_stars")],
            [InlineKeyboardButton(text="👤 Профиль юзера", callback_data="admin_view_user")],
            [InlineKeyboardButton(text="❓ Управление вопросами", callback_data="admin_questions")]
        ]
    )

def get_questions_admin_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Добавить вопрос", callback_data="admin_add_q")],
            [InlineKeyboardButton(text="Удалить вопрос", callback_data="admin_del_q")],
            [InlineKeyboardButton(text="Изменить вопрос", callback_data="admin_edit_q")]
        ]
    )