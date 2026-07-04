from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import get_user, get_random_question, update_balance, update_last_task, add_reward_log, get_top_users
from keyboards.menu import get_categories_menu, get_main_menu
from utils.cooldown import check_cooldown
from utils.rewards import generate_reward
import asyncio

router = Router()

class TaskState(StatesGroup):
    waiting_for_answer = State()

@router.message(F.text == "🔙 Назад")
async def btn_back(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Возврат в главное меню.", reply_markup=get_main_menu())

@router.message(F.text == "ℹ️ Правила")
async def btn_rules(message: Message):
    rules = (
        "<b>Правила бота:</b>\n"
        "1. Раз в 24 часа вы можете выбрать категорию и ответить на случайный вопрос.\n"
        "2. За правильный ответ вы получите от 1 до 5 Stars ⭐️.\n"
        "3. Если ответ неверный, попробовать снова можно будет только на следующий день.\n"
        "4. Администрация может отправлять вам подарки за накопленные Stars."
    )
    await message.answer(rules, parse_mode="HTML")

@router.message(F.text == "🏆 Топ пользователей")
async def btn_top(message: Message):
    top = await get_top_users()
    if not top:
        await message.answer("Топ пока пуст.")
        return
    
    text = "<b>🏆 Топ-10 пользователей:</b>\n\n"
    for i, (username, balance) in enumerate(top, 1):
        text += f"{i}. @{username} — {balance} ⭐️\n"
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "👤 Профиль")
async def btn_profile(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        return
    
    _, _, username, balance, last_task, reg_date = user
    can_do, time_left = check_cooldown(last_task)
    status = "✅ Готов к выполнению" if can_do else f"⏳ Ожидание: {time_left}"
    
    text = (
        f"<b>👤 Профиль пользователя</b>\n"
        f"├ <b>ID:</b> <code>{message.from_user.id}</code>\n"
        f"├ <b>Username:</b> @{username}\n"
        f"├ <b>Баланс:</b> {balance} ⭐️\n"
        f"└ <b>Статус задания:</b> {status}"
    )
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "📚 Задания")
async def btn_tasks(message: Message):
    user = await get_user(message.from_user.id)
    can_do, time_left = check_cooldown(user[4])
    
    if not can_do:
        await message.answer(f"Следующее задание будет доступно через:\n<b>{time_left}</b>", parse_mode="HTML")
        return
        
    await message.answer("Выберите категорию вопросов:", reply_markup=get_categories_menu())

@router.message(F.text.in_(["➕ Математика", "📜 История России", "📚 Русский язык", "🧠 Логика", "🌍 География России"]))
async def select_category(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    can_do, time_left = check_cooldown(user[4])
    if not can_do:
        await message.answer(f"Задание недоступно. Ждать: {time_left}")
        return

    question = await get_random_question(message.text)
    if not question:
        await message.answer("В этой категории пока нет вопросов.")
        return

    await state.update_data(answer=question[3].lower().strip())
    
    msg = await message.answer("⏳ Готовим вопрос...", reply_markup=get_main_menu())
    await asyncio.sleep(1)
    
    await msg.edit_text(f"<b>Категория: {message.text}</b>\n\nВопрос:\n<i>{question[2]}</i>\n\nНапишите ваш ответ в чат:", parse_mode="HTML")
    await state.set_state(TaskState.waiting_for_answer)

@router.message(TaskState.waiting_for_answer)
async def check_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    correct_answer = data.get("answer")
    user_answer = message.text.lower().strip()
    
    await update_last_task(message.from_user.id)
    await state.clear()
    
    if user_answer == correct_answer:
        stars = generate_reward()
        await update_balance(message.from_user.id, stars)
        await add_reward_log(message.from_user.id, stars)
        await message.answer(f"🎉 <b>Поздравляем!</b> Ответ верный.\nВы получили случайную награду: <b>{stars} ⭐️</b>", parse_mode="HTML")
    else:
        await message.answer("❌ <b>Ответ неверный.</b>\nПравильный ответ мы сохраним в секрете.\nПопробуйте завтра!", parse_mode="HTML")