from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
import requests
from config import API_BASE_URL

router = Router()

# Nechta buyurtma bir sahifada ko'rsatiladi
ORDERS_PER_PAGE = 5

@router.message(lambda msg: msg.text in ["📄 Buyurtmalarim", "📄 Мои заказы"])
async def my_orders(msg: Message, state: FSMContext):
    # Foydalanuvchi tilini aniqlash
    user_language = "ru" if msg.text == "📄 Мои заказы" else "uz"
    await state.update_data(language=user_language)
    await show_orders_page(msg, state, page=0)

@router.callback_query(F.data.startswith("orders_page_"))
async def paginate_orders(call: CallbackQuery, state: FSMContext):
    page = int(call.data.replace("orders_page_", ""))
    await call.message.delete()
    await show_orders_page(call.message, state, page)

async def show_orders_page(target, state: FSMContext, page: int):
    try:
        user_language = await get_user_language(state)
        tg_user_id = target.from_user.id

        # 1. Foydalanuvchi
        users = requests.get(f"{API_BASE_URL}/users/").json()
        user = next((u for u in users if u["user_id"] == tg_user_id), None)
        if not user:
            error_msg = "❌ Пользователь не найден." if user_language == "ru" else "❌ Foydalanuvchi topilmadi."
            await target.answer(error_msg)
            return

        user_id = user["id"]

        # 2. Buyurtmalar
        all_orders = requests.get(f"{API_BASE_URL}/orders/").json()
        user_orders = [o for o in all_orders if o["user"] == user_id]
        if not user_orders:
            empty_msg = "📭 У вас пока нет заказов." if user_language == "ru" else "📭 Sizda hali hech qanday buyurtma yo'q."
            await target.answer(empty_msg)
            return

        products = requests.get(f"{API_BASE_URL}/products/").json()
        colors = requests.get(f"{API_BASE_URL}/colors/").json()
        sizes = requests.get(f"{API_BASE_URL}/sizes/").json()
        
        # Ruscha nomlar mavjud bo'lsa, ularni ishlatamiz
        color_map = {c["id"]: c.get("name_ru", c["name"]) if user_language == "ru" else c["name"] for c in colors}
        size_map = {s["id"]: s.get("name_ru", s["name"]) if user_language == "ru" else s["name"] for s in sizes}

        total_pages = (len(user_orders) + ORDERS_PER_PAGE - 1) // ORDERS_PER_PAGE
        page = max(0, min(page, total_pages - 1))  # chegaralash

        start = page * ORDERS_PER_PAGE
        end = start + ORDERS_PER_PAGE
        current_orders = sorted(user_orders, key=lambda x: x.get("id", 0), reverse=True)[start:end]

        # Matnlarni tilga qarab tanlash
        texts = {
            "uz": {
                "title": "📄 Buyurtmalarim (sahifa {page}/{total_pages}):",
                "order_id": "🆔 Buyurtma #{id}",
                "phone": "📱 Telefon:",
                "status": "📦 Status:",
                "price": "{price:,} so'm x {number} dona = <b>{summa:,} so'm</b>",
                "color": "🎨 Rang:",
                "size": "📏 Razmer:",
                "prev": "⏪ Orqaga",
                "next": "⏩ Keyingi",
                "unknown": "Noma'lum"
            },
            "ru": {
                "title": "📄 Мои заказы (страница {page}/{total_pages}):",
                "order_id": "🆔 Заказ #{id}",
                "phone": "📱 Телефон:",
                "status": "📦 Статус:",
                "price": "{price:,} сум x {number} шт = <b>{summa:,} сум</b>",
                "color": "🎨 Цвет:",
                "size": "📏 Размер:",
                "prev": "⏪ Назад",
                "next": "⏩ Вперед",
                "unknown": "Неизвестно"
            }
        }[user_language]

        text = f"<b>{texts['title'].format(page=page+1, total_pages=total_pages)}</b>\n\n"
        
        for order in current_orders:
            text += f"{texts['order_id'].format(id=order['id'])}\n"
            text += f"{texts['phone']} {order['phone']}\n"
            
            # Statusni tarjima qilish
            status_map = {
                "uz": {
                    "new": "Yangi",
                    "processing": "Jarayonda",
                    "completed": "Yakunlangan",
                    "cancelled": "Bekor qilingan"
                },
                "ru": {
                    "new": "Новый",
                    "processing": "В обработке",
                    "completed": "Завершен",
                    "cancelled": "Отменен"
                }
            }[user_language]
            
            status = status_map.get(order['status'].lower(), order['status'].capitalize())
            text += f"{texts['status']} <b>{status}</b>\n"

            for d in order.get("details", []):
                product_id = d["product"]
                number = d["number"]
                color_id = d.get("color")
                size_id = d.get("size")
                color = color_map.get(color_id, texts["unknown"])
                size = size_map.get(size_id, texts["unknown"])

                product = next((p for p in products if p["id"] == product_id), None)
                if product:
                    name = product.get("product_name_ru", product["product_name"]) if user_language == "ru" else product["product_name"]
                    price = product["price"]
                    summa = price * number
                    text += (
                        f"🛒 <b>{name}</b>\n"
                        f"💵 {texts['price'].format(price=price, number=number, summa=summa)}\n"
                        f"{texts['color']} {color}\n"
                        f"{texts['size']} {size}\n\n"
                    )
                else:
                    text += (
                        f"🛒 Product ID: {product_id}\n"
                        f"Soni: {number} dona, {texts['color']}: {color}, {texts['size']}: {size}\n"
                    )

            text += f"──────────────\n\n"

        # Inline tugmalar
        buttons = []
        if page > 0:
            buttons.append(InlineKeyboardButton(text=texts["prev"], callback_data=f"orders_page_{page-1}"))
        if page < total_pages - 1:
            buttons.append(InlineKeyboardButton(text=texts["next"], callback_data=f"orders_page_{page+1}"))

        markup = InlineKeyboardMarkup(inline_keyboard=[buttons]) if buttons else None

        await target.answer(text, reply_markup=markup)

    except Exception as e:
        print("❌ Buyurtmalarni olishda xatolik:", e)
        error_msg = "❌ Ошибка при получении заказов." if user_language == "ru" else "❌ Buyurtmalarni olishda xatolik yuz berdi."
        await target.answer(error_msg)

async def get_user_language(state: FSMContext) -> str:
    """Foydalanuvchi tilini olish"""
    data = await state.get_data()
    return data.get("language", "uz")