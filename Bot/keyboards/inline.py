from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def language_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O‘zbek", callback_data="lang_uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")]
    ])

def language_buttonsss():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O‘zbek", callback_data="lang_uzz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ruu")]
    ])
