from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from Bot.keyboards.inline import language_buttonsss
from Bot.states import SettingsState
from Bot.utils.api import get_user_by_id, update_user_field

router = Router()

def settings_keyboard(language: str = "uz"):
    texts = {
        "uz": {
            "edit_name": "✏️ Ismni o‘zgartirish",
            "edit_phone": "📞 Telefon raqamni o‘zgartirish",
            "edit_lang": "🌐 Tilni o‘zgartirish"
        },
        "ru": {
            "edit_name": "✏️ Изменить имя",
            "edit_phone": "📞 Изменить телефон",
            "edit_lang": "🌐 Изменить язык"
        }
    }[language]
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts["edit_name"], callback_data="edit_fullname")],
        [InlineKeyboardButton(text=texts["edit_phone"], callback_data="edit_phone")],
        [InlineKeyboardButton(text=texts["edit_lang"], callback_data="edit_lang")],
    ])

@router.callback_query(F.data == "edit_lang")
async def lkjhgs(call:CallbackQuery):
    await call.message.delete()
    await call.message.answer(
            "👋 Assalomu alaykum!\n👋 Привет!\n\n"
            "Tilni tanlang / Выберите язык",
            reply_markup=language_buttonsss()
        )



@router.message(lambda msg: msg.text in ["⚙️ Sozlamalar", "⚙️ Настройки"])
async def settings_menu(msg: Message, state: FSMContext):
    # Foydalanuvchi tilini aniqlash
    user_language = "ru" if msg.text == "⚙️ Настройки" else "uz"
    await state.update_data(language=user_language)
    
    user = get_user_by_id(msg.from_user.id)
    if not user:
        error_msg = "❌ Настройки не найдены." if user_language == "ru" else "❌ Sozlamalar topilmadi."
        await msg.answer(error_msg)
        return
    
    # Matnlarni tilga qarab tanlash
    texts = {
        "uz": {
            "title": "⚙️ Sizning profil ma'lumotlaringiz:",
            "name": "👤 F.I.O:",
            "phone": "📱 Telefon:",
            "username": "🔗 Username:",

        },
        "ru": {
            "title": "⚙️ Ваши профильные данные:",
            "name": "👤 Ф.И.О:",
            "phone": "📱 Телефон:",
            "username": "🔗 Username:",

        }
    }[user_language]
    
    text = (
        f"<b>{texts['title']}</b>\n\n"
        f"{texts['name']} {user.get('user_fullname')}\n"
        f"{texts['phone']} {user.get('user_phone')}\n"
        f"{texts['username']} @{user.get('user_username') or 'yo‘q'}\n"
    )
    await msg.answer(text, reply_markup=settings_keyboard(user_language))

@router.callback_query(F.data == "edit_fullname")
async def edit_fullname_prompt(call: CallbackQuery, state: FSMContext):
    user_language = await get_user_language(state)
    prompt = "✏️ Введите новое Ф.И.О:" if user_language == "ru" else "✏️ Yangi F.I.O. ni yuboring:"
    await call.message.answer(prompt)
    await state.set_state(SettingsState.full_name)

@router.callback_query(F.data == "edit_phone")
async def edit_phone_prompt(call: CallbackQuery, state: FSMContext):
    user_language = await get_user_language(state)
    prompt = "📞 Введите новый номер телефона:" if user_language == "ru" else "📞 Yangi telefon raqamni yuboring:"
    await call.message.answer(prompt)
    await state.set_state(SettingsState.phone)

@router.message(SettingsState.full_name)
async def save_fullname(msg: Message, state: FSMContext):
    user_language = await get_user_language(state)
    if update_user_field(msg.from_user.id, "user_fullname", msg.text):
        success_msg = "✅ Ф.И.О. обновлено." if user_language == "ru" else "✅ F.I.O yangilandi."
        await msg.answer(success_msg)
    else:
        error_msg = "❌ Ошибка при обновлении." if user_language == "ru" else "❌ Yangilashda xatolik."
        await msg.answer(error_msg)
    await state.clear()

@router.message(SettingsState.phone)
async def save_phone(msg: Message, state: FSMContext):
    user_language = await get_user_language(state)
    if update_user_field(msg.from_user.id, "user_phone", msg.text):
        success_msg = "✅ Телефон обновлен." if user_language == "ru" else "✅ Telefon raqam yangilandi."
        await msg.answer(success_msg)
    else:
        error_msg = "❌ Ошибка при обновлении." if user_language == "ru" else "❌ Yangilashda xatolik."
        await msg.answer(error_msg)
    await state.clear()



async def get_user_language(state: FSMContext) -> str:
    """Foydalanuvchi tilini olish"""
    data = await state.get_data()
    return data.get("language", "uz")