from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_ID
from keyboards.menu import get_admin_menu, get_questions_admin_menu
from database import get_all_users, get_user, update_balance
import aiosqlite

router = Router()

class AdminState(StatesGroup):
    broadcast_text = State()
    target_user_id = State()
    add_stars_amount = State()
    del_stars_amount = State()
    add_q_category = State()
    add_q_text = State()
    add_q_answer = State()
    del_q_id = State()

def is_admin(user_id: int):
    return user_id == ADMIN_ID

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("🛠 <b>Панель администратора</b>", reply_markup=get_admin_menu(), parse_mode="HTML")

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id): return
    users = await get_all_users()
    await callback.message.answer(f"📊 <b>Статистика:</b>\nВсего пользователей: {len(users)}", parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id): return
    await callback.message.answer("Введите текст для рассылки (поддерживается HTML):")
    await state.set_state(AdminState.broadcast_text)
    await callback.answer()

@router.message(AdminState.broadcast_text)
async def process_broadcast(message: Message, state: FSMContext, bot: Bot):
    users = await get_all_users()
    count = 0
    await message.answer("⏳ Начинаю рассылку...")
    for u in users:
        try:
            await bot.send_message(u[0], message.text, parse_mode="HTML")
            count += 1
        except Exception:
            pass
    await message.answer(f"✅ Рассылка завершена. Доставлено: {count} пользователям.")
    await state.clear()

@router.callback_query(F.data == "admin_add_stars")
async def admin_add_stars_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id): return
    await callback.message.answer("Введите ID пользователя (Telegram ID):")
    await state.set_state(AdminState.target_user_id)
    await state.update_data(action="add")
    await callback.answer()

@router.callback_query(F.data == "admin_del_stars")
async def admin_del_stars_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id): return
    await callback.message.answer("Введите ID пользователя (Telegram ID):")
    await state.set_state(AdminState.target_user_id)
    await state.update_data(action="del")
    await callback.answer()

@router.callback_query(F.data == "admin_view_user")
async def admin_view_user(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id): return
    await callback.message.answer("Введите ID пользователя (Telegram ID):")
    await state.set_state(AdminState.target_user_id)
    await state.update_data(action="view")
    await callback.answer()

@router.message(AdminState.target_user_id)
async def admin_target_user(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
    except ValueError:
        await message.answer("ID должен быть числом.")
        return
    
    user = await get_user(user_id)
    if not user:
        await message.answer("Пользователь не найден в БД.")
        await state.clear()
        return

    data = await state.get_data()
    action = data.get("action")
    
    if action == "view":
        text = f"👤 <b>Профиль</b>\nID: {user[1]}\nUsername: @{user[2]}\nБаланс: {user[3]}\nРегистрация: {user[5]}"
        await message.answer(text, parse_mode="HTML")
        await state.clear()
    else:
        await state.update_data(target_id=user_id)
        await message.answer(f"Введите количество Stars для {'начисления' if action=='add' else 'списания'}:")
        await state.set_state(AdminState.add_stars_amount if action == "add" else AdminState.del_stars_amount)

@router.message(AdminState.add_stars_amount)
async def process_add_stars(message: Message, state: FSMContext):
    try: amount = int(message.text)
    except: return await message.answer("Введите число.")
    
    data = await state.get_data()
    await update_balance(data["target_id"], amount)
    await message.answer(f"✅ Баланс пользователя {data['target_id']} пополнен на {amount} Stars.")
    await state.clear()

@router.message(AdminState.del_stars_amount)
async def process_del_stars(message: Message, state: FSMContext):
    try: amount = int(message.text)
    except: return await message.answer("Введите число.")
    
    data = await state.get_data()
    await update_balance(data["target_id"], -amount)
    await message.answer(f"✅ У пользователя {data['target_id']} списано {amount} Stars.")
    await state.clear()

@router.callback_query(F.data == "admin_questions")
async def admin_questions(callback: CallbackQuery):
    if not is_admin(callback.from_user.id): return
    await callback.message.answer("Управление вопросами:", reply_markup=get_questions_admin_menu())
    await callback.answer()

# Здесь можно расширить стейты для добавления и удаления вопросов (add_q, del_q).
# Для примера реализовано базовое меню, полная реализация требует аналогичных стейт-машин.