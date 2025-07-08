from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from Bot.keyboards.inline import language_buttonsss, language_buttons
from Bot.keyboards.reply import main_menu_keyboard, main_menu_keyboard_ru
from Bot.states import RegisterState, RegisterStateRu
from Bot.utils.api import check_user_exists

router = Router()

@router.message(CommandStart())
async def start_command(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    if check_user_exists(user_id):
        await msg.answer(
            "👋 Assalomu alaykum!\n👋 Привет!\n\n"
            "Tilni tanlang / Выберите язык",
            reply_markup=language_buttonsss()
        )
    else:
        await msg.answer("Tilni tanlang / Выберите язык", reply_markup=language_buttons())

@router.callback_query(F.data == "lang_uz")
async def lang_selected(call: CallbackQuery, state: FSMContext):
    lang = call.data.split("_")[1]  # => "uz"
    await state.update_data(language=lang)
    await call.message.edit_text("Iltimos, to‘liq ism-sharifingizni kiriting:")
    await state.set_state(RegisterState.fullname)

@router.callback_query(F.data == "lang_ru")
async def lang_ru(call: CallbackQuery, state: FSMContext):
    lang = call.data.split("_")[1]  # => "ru"
    await state.update_data(lang=lang)
    await call.message.answer("Пожалуйста, введите свое полное имя")
    await state.set_state(RegisterStateRu.fullname)



@router.callback_query(F.data == "lang_uzz")
async def lang_ru(call: CallbackQuery):
    await call.message.answer("Marhamat, bosh menu", reply_markup=main_menu_keyboard())


@router.callback_query(F.data == "lang_ruu")
async def lang_ru(call: CallbackQuery):
    await call.message.answer("Благословение, главное меню", reply_markup=main_menu_keyboard_ru())