from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def generate_quantity_keyboard(product_id: int, quantity: int, price: int, category_slug: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➖", callback_data=f"decrease_{product_id}"),
            InlineKeyboardButton(text=f"{quantity} dona", callback_data="quantity_ignore"),
            InlineKeyboardButton(text="➕", callback_data=f"increase_{product_id}")
        ],
        [
            InlineKeyboardButton(
                text=f"🛒 Savatga qo‘shish ({quantity * price:,} so'm)",
                callback_data=f"addbasket_{product_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🖼 Rasmni joylash",
                callback_data=f"uploadphoto_{product_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 Orqaga", callback_data=f"category_{category_slug}"  # ← bu MUHIM
            )
        ]
    ])
