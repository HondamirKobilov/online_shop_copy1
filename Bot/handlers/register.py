from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from Bot.keyboards.reply import main_menu_keyboard, main_menu_keyboard_ru
from Bot.states import RegisterState, RegisterStateRu
from Bot.utils.api import register_user

router = Router()

@router.message(RegisterState.fullname)
async def get_fullname(msg: Message, state: FSMContext):
    await state.update_data(user_fullname=msg.text)
    contact_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await msg.answer("Iltimos, telefon raqamingizni yuboring:", reply_markup=contact_kb)
    await state.set_state(RegisterState.phone)

@router.message(RegisterState.phone)
async def get_phone(msg: Message, state: FSMContext):
    if not msg.contact:
        await msg.answer("Iltimos, tugma orqali telefon raqam yuboring.")
        return
    await state.update_data(user_phone=msg.contact.phone_number)
    data = await state.get_data()

    user_data = {
        "user_id": msg.from_user.id,
        "user_username": msg.from_user.username,
        "user_fullname": data["user_fullname"],
        "user_phone": data["user_phone"],
        "language": data["language"]
    }

    if register_user(user_data):
        await msg.answer("✅ Ro'yxatdan muvaffaqiyatli o'tdingiz!", reply_markup=main_menu_keyboard())
    else:
        await msg.answer("❌ Xatolik yuz berdi. Keyinroq urinib ko‘ring.", reply_markup=ReplyKeyboardRemove())

    await state.clear()

    #ru register


@router.message(RegisterStateRu.fullname)
async def get_fullname(msg: Message, state: FSMContext):
    await state.update_data(fullname=msg.text)
    contact_kbb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await msg.answer("Пожалуйста, отправьте свой номер телефона:", reply_markup=contact_kbb)
    await state.set_state(RegisterStateRu.phone)

@router.message(RegisterStateRu.phone)
async def get_phone(msg: Message, state: FSMContext):
    if not msg.contact:
        await msg.answer("Пожалуйста, отправьте номер телефона через кнопку.")
        return
    await state.update_data(phone=msg.contact.phone_number)
    data = await state.get_data()

    user_data = {
        "user_id": msg.from_user.id,
        "user_username": msg.from_user.username,
        "user_fullname": data["fullname"],
        "user_phone": data["phone"],
        "language": data["lang"]
    }

    if register_user(user_data):
        await msg.answer("✅ Вы успешно зарегистрировались!", reply_markup=main_menu_keyboard_ru())
    else:
        await msg.answer("❌ Произошла ошибка. Попробуйте позже.", reply_markup=ReplyKeyboardRemove())

    await state.clear()




