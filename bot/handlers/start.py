from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from config import CHANNELS
from database import add_user
from keyboards.menu import get_subscription_menu, get_main_menu
import asyncio

router = Router()

async def check_user_subs(bot: Bot, user_id: int):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception:
            # Если бот не админ в канале, он не сможет проверить
            return False
    return True

@router.message(Command("start"))
async def cmd_start(message: Message, bot: Bot):
    await add_user(message.from_user.id, message.from_user.username or "Без имени")
    
    is_subscribed = await check_user_subs(bot, message.from_user.id)
    
    text = (
        "<b>Добро пожаловать!</b> ✨\n\n"
        "Здесь ты можешь получать <b>Telegram Stars</b> каждый день.\n"
        "Для начала необходимо выполнить условия: подпишись на наши каналы."
    )
    
    try:
        photo = FSInputFile("images/welcome.jpg")
        await message.answer_photo(
            photo=photo, 
            caption=text, 
            parse_mode="HTML", 
            reply_markup=get_subscription_menu()
        )
    except Exception:
        # Fallback если нет картинки
        await message.answer(text, parse_mode="HTML", reply_markup=get_subscription_menu())

@router.callback_query(F.data == "check_sub")
async def process_sub_check(callback: CallbackQuery, bot: Bot):
    await callback.message.edit_caption(caption="⏳ Проверяем подписки...", reply_markup=None)
    await asyncio.sleep(1) # Имитация загрузки
    
    is_subscribed = await check_user_subs(bot, callback.from_user.id)
    if is_subscribed:
        await callback.message.delete()
        await callback.message.answer(
            "🎉 Отлично! Вы подписаны на все каналы.\nДобро пожаловать в главное меню!",
            reply_markup=get_main_menu()
        )
    else:
        await callback.message.edit_caption(
            caption="❌ Сначала подпишитесь на все каналы.",
            reply_markup=get_subscription_menu()
        )
    await callback.answer()