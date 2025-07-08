from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Mahsulotlar")],
            [KeyboardButton(text="📄 Buyurtmalarim"), KeyboardButton(text="🔵 Ijtimoiy tarmoq")],
            [KeyboardButton(text="⚙️ Sozlamalar"), KeyboardButton(text="🛒 Savat")],
            [KeyboardButton(text="📞 Bog'lanish")]
        ],
        resize_keyboard=True
    )


def main_menu_keyboard_ru():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Продукты")],
            [KeyboardButton(text="📄 Мои заказы"), KeyboardButton(text="🔵 Социальная сеть")],
            [KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="🛒 Корзина")],
            [KeyboardButton(text="📞 Связь")]
        ],
        resize_keyboard=True
    )
