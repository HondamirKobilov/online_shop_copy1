from aiogram import Router, F, Bot
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    LabeledPrice, PreCheckoutQuery, KeyboardButton
)
from aiogram.fsm.context import FSMContext

from Bot.config import CHANNEL_CHAT_ID, API_BASE_URL
from Bot.utils.api import get_user_by_id
from aiogram.enums import ParseMode
import traceback
# from config import API_BASE_URL
import requests

router = Router()

# Har bir sahifada ko'rsatiladigan buyurtmalar soni
ORDERS_PER_PAGE = 5

def get_user_language(text: str) -> str:
    """Foydalanuvchi tilini aniqlash"""
    return "ru" if text in ["🛒 Корзина", "📞 Контакты", "⚙️ Настройки"] else "uz"

async def get_user_language_from_state(source) -> str:
    """Foydalanuvchi tilini state yoki xabardan olish"""
    if isinstance(source, FSMContext):
        data = await source.get_data()
        return data.get("language", "uz")
    elif isinstance(source, (Message, CallbackQuery)):
        if hasattr(source, 'text'):
            return get_user_language(source.text)
        elif hasattr(source, 'data') and source.data == "confirm_order":
            data = await source.state.get_data()
            return data.get("language", "uz")
    return "uz"

@router.message(lambda msg: msg.text in ["🛒 Savat", "🛒 Корзина"])
async def show_basket(msg: Message, state: FSMContext):
    user_language = get_user_language(msg.text)
    await state.update_data(language=user_language)
    
    user = get_user_by_id(msg.from_user.id)
    if not user:
        error_msg = "❌ Пользователь не найден." if user_language == "ru" else "❌ Foydalanuvchi topilmadi."
        await msg.answer(error_msg)
        return

    try:
        res = requests.get(f"{API_BASE_URL}/baskets/")
        res.raise_for_status()
        all_baskets = res.json()
        user_baskets = [b for b in all_baskets if b.get("user", {}).get("user_id") == msg.from_user.id]

        if not user_baskets:
            empty_msg = "🛒 Ваша корзина пуста." if user_language == "ru" else "🛒 Savatingiz bo'sh."
            await msg.answer(empty_msg)
            return

        # Matnlarni tilga qarab tanlash
        texts = {
            "uz": {
                "title": "🛍 Savatingizdagi mahsulotlar:",
                "color": "🎨 Rang:",
                "size": "📏 Razmer:",
                "quantity": "🔢 Soni:",
                "price": "💵 Narxi:",
                "total_item": "🧮 Jami:",
                "grand_total": "📻 Umumiy:",
                "confirm": "✅ Tasdiqlash",
                "cancel": "❌ Rad etish",
                "unknown": "Noma'lum"
            },
            "ru": {
                "title": "🛍 Товары в вашей корзине:",
                "color": "🎨 Цвет:",
                "size": "📏 Размер:",
                "quantity": "🔢 Количество:",
                "price": "💵 Цена:",
                "total_item": "🧮 Итого:",
                "grand_total": "📻 Общая сумма:",
                "confirm": "✅ Подтвердить",
                "cancel": "❌ Отменить",
                "unknown": "Неизвестно"
            }
        }[user_language]

        text = f"<b>{texts['title']}</b>\n\n"
        total = 0
        
        for b in user_baskets:
            product = b.get("product", {})
            color = b.get("color")
            size = b.get("size")
            
            # Rang va o'lcham nomlarini xavfsiz olish
            color_name = color.get('name_ru' if user_language == 'ru' else 'name', texts["unknown"]) if color else texts["unknown"]
            size_name = size.get('name_ru' if user_language == 'ru' else 'name', texts["unknown"]) if size else texts["unknown"]

            color_text = f"{texts['color']} {color_name}" if color else ""
            size_text = f"{texts['size']} {size_name}" if size else ""

            product_name = product.get('product_name_ru' if user_language == 'ru' else 'product_name', f"Mahsulot ID: {product.get('id', '?')}")
            price = product.get("price", 0)
            quantity = b.get("number", 0)
            item_total = price * quantity
            total += item_total
            
            text += (
                f"📦 <b>{product_name}</b>\n"
                f"{color_text}\n"
                f"{size_text}\n"
                f"{texts['quantity']} {quantity} dona\n"
                f"{texts['price']} {price:,} so'm\n"
                f"{texts['total_item']} <b>{item_total:,} so'm</b>\n\n"
            )

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=texts["confirm"], callback_data="confirm_order")],
            [InlineKeyboardButton(text=texts["cancel"], callback_data="cancel_order")]
        ])

        await msg.answer(text + f"{texts['grand_total']} <b>{total:,} so'm</b>", reply_markup=markup)

    except requests.exceptions.RequestException as e:
        print(f"❌ API so'rovida xatolik: {e}")
        error_msg = "❌ Ошибка при загрузке корзины." if user_language == "ru" else "❌ Savatni yuklashda xatolik yuz berdi."
        await msg.answer(error_msg)
    except Exception as e:
        print(f"❌ Umumiy xatolik: {str(e)}")
        error_msg = "❌ Произошла ошибка." if user_language == "ru" else "❌ Xatolik yuz berdi."
        await msg.answer(error_msg)


@router.callback_query(F.data == "confirm_order")
async def confirm_order_handler(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_data = get_user_by_id(user_id)
    if not user_data:
        await callback.message.answer("❌ Foydalanuvchi topilmadi.")
        return

    # API orqali barcha savatlarni olish
    try:
        res = requests.get(f"{API_BASE_URL}/baskets/")
        res.raise_for_status()
        all_baskets = res.json()
        user_baskets = [b for b in all_baskets if b.get("user", {}).get("user_id") == user_id]

        if not user_baskets:
            await callback.message.answer("❌ <b>Savatingiz bo‘sh.</b>", parse_mode=ParseMode.HTML)
            return

        # Xabar dizayni
        text = "<b>🛍 Yangi buyurtma!</b>\n\n"
        total = 0

        for idx, b in enumerate(user_baskets, start=1):
            product = b.get("product", {})
            color = b.get("color")
            size = b.get("size")

            color_name = color.get("name", "Noma'lum") if color else "Noma'lum"
            size_name = size.get("name", "Noma'lum") if size else "Noma'lum"
            product_name = product.get("product_name", f"Mahsulot ID: {product.get('id', '?')}")
            price = product.get("price", 0)
            quantity = b.get("number", 0)
            item_total = price * quantity
            total += item_total

            text += (
                f"<b>{idx}. {product_name}</b>\n"
                f"🎨 Rang: {color_name}\n"
                f"📏 Razmer: {size_name}\n"
                f"🔢 Soni: {quantity} dona\n"
                f"💵 Narxi: {price:,} so‘m\n"
                f"🧮 Jami: <b>{item_total:,} so‘m</b>\n\n"
            )

        text += f"<b>📻 Umumiy:</b> <code>{total:,}</code> so‘m\n"
        text += f"\n📞 Tel: <code>{user_data.get('phone_number', 'ko‘rsatilmagan')}</code>"
        # Kanalga yuborish
        await callback.bot.send_message(
            chat_id=CHANNEL_CHAT_ID,  # o‘rniga kanal chat_id sini yoz
            text=text,
            parse_mode=ParseMode.HTML
        )

        # Foydalanuvchiga xabar
        await callback.message.answer("✅ Buyurtmangiz qabul qilindi va adminlarga yuborildi.")

    except requests.exceptions.RequestException as e:
        print(f"❌ API xatosi: {e}")
        await callback.message.answer("❌ Savat ma'lumotlarini olishda xatolik.")
    except Exception as e:
        print("❌ Xatolik:", e)
        print(traceback.format_exc())  # Bu to‘liq xatolikni chiqaradi
        await callback.message.answer(f"❌ Buyurtmani yuborishda xatolik: {e}")


# @router.callback_query(F.data == "confirm_order")
# async def confirm_order(call: CallbackQuery, state: FSMContext):
#     user_language = await get_user_language_from_state(state)
#
#     try:
#         user = get_user_by_id(call.from_user.id)
#         if not user:
#             error_msg = "❌ Пользователь не найден." if user_language == "ru" else "❌ Foydalanuvchi topilmadi."
#             await call.message.answer(error_msg)
#             return
#
#         res = requests.get(f"{API_BASE_URL}/baskets/")
#         res.raise_for_status()
#         all_baskets = res.json()
#         user_baskets = [b for b in all_baskets if b.get("user", {}).get("user_id") == call.from_user.id]
#
#         if not user_baskets:
#             empty_msg = "🛒 Ваша корзина пуста." if user_language == "ru" else "🛒 Savatingiz bo'sh."
#             await call.message.answer(empty_msg)
#             return
#
#         order_details = []
#         total_price = 0
#
#         for b in user_baskets:
#             product = b.get("product", {})
#             if not product:
#                 continue
#
#             color = b.get("color") or {}
#             size = b.get("size") or {}
#
#             order_details.append({
#                 "product": product.get("id"),
#                 "number": b.get("number", 0),
#                 "color": color.get("id") if color else None,
#                 "size": size.get("id") if size else None
#             })
#
#             total_price += product.get("price", 0) * b.get("number", 0)
#
#         if total_price <= 0:
#             error_msg = "❌ Общая сумма заказа должна быть больше 0." if user_language == "ru" else "❌ Buyurtma summasi 0 dan katta bo'lishi kerak."
#             await call.message.answer(error_msg)
#             return
#
#         await state.update_data(
#             user_id=user.get("id"),
#             user_phone=user.get("user_phone"),
#             order_details=order_details,
#             total_price=total_price
#         )
#
#         label = "Оплата корзины" if user_language == "ru" else "Savat to'lovi"
#         title = "Оплата заказа" if user_language == "ru" else "Buyurtma to'lovi"
#         description = "Оплата товаров" if user_language == "ru" else "Mahsulotlar uchun to'lov"
#
#         await call.message.answer_invoice(
#             title=title,
#             description=description,
#             provider_token="387026696:LIVE:68233ecd719315ab299f65c8",
#             #provider_token="398062629:TEST:999999999_F91D8F69C042267444B74CC0B3C747757EB0E065",
#             currency="UZS",
#             prices=[LabeledPrice(label=label, amount=int(total_price * 100))],
#             payload="buyurtma_tolov",
#             start_parameter="buyurtma-start",
#             need_phone_number=True,
#             need_name=True
#         )
#
#     except requests.exceptions.RequestException as e:
#         print(f"❌ API so'rovida xatolik: {e}")
#         error_msg = "❌ Ошибка при запуске платежа." if user_language == "ru" else "❌ To'lovni boshlashda xatolik yuz berdi."
#         await call.message.answer(error_msg)
#     except Exception as e:
#         print(f"❌ Umumiy xatolik: {str(e)}")
#         error_msg = "❌ Произошла ошибка." if user_language == "ru" else "❌ Xatolik yuz berdi."
#         await call.message.answer(error_msg)


@router.callback_query(F.data == "cancel_order")
async def cancel_order(call: CallbackQuery, state: FSMContext):
    user_language = await get_user_language_from_state(state)
    
    try:
        res = requests.get(f"{API_BASE_URL}/baskets/")
        res.raise_for_status()
        all_baskets = res.json()
        user_baskets = [b for b in all_baskets if b.get("user", {}).get("user_id") == call.from_user.id]

        for b in user_baskets:
            del_res = requests.delete(f"{API_BASE_URL}/baskets/{b.get('id')}/")
            del_res.raise_for_status()

        success_msg = "❌ Заказ отменен и корзина очищена." if user_language == "ru" else "❌ Buyurtma bekor qilindi va savat tozalandi."
        await call.message.answer(success_msg)

    except requests.exceptions.RequestException as e:
        print(f"❌ API so'rovida xatolik: {e}")
        error_msg = "❌ Ошибка при отмене." if user_language == "ru" else "❌ Bekor qilishda xatolik yuz berdi."
        await call.message.answer(error_msg)
    except Exception as e:
        print(f"❌ Umumiy xatolik: {str(e)}")
        error_msg = "❌ Произошла ошибка." if user_language == "ru" else "❌ Xatolik yuz berdi."
        await call.message.answer(error_msg)

@router.pre_checkout_query()
async def process_checkout_query(query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


@router.message(F.successful_payment)
async def process_successful_payment(message: Message, state: FSMContext):
    user_language = await get_user_language_from_state(state)
    data = await state.get_data()
    user_id = data.get("user_id")
    user_phone = data.get("user_phone")
    order_details = data.get("order_details")

    payload = {
        "user": user_id,
        "phone": user_phone,
        "status": "accept",
        "details": order_details
    }

    try:
        res = requests.post(f"{API_BASE_URL}/orders/", json=payload)
        if res.status_code not in [200, 201]:
            print("❌ Order API error:", res.status_code, res.text)
            error_msg = "❌ Ошибка при сохранении заказа." if user_language == "ru" else "❌ Buyurtmani saqlashda xatolik yuz berdi."
            await message.answer(error_msg)
            return

        # Savatni tozalash
        all_baskets = requests.get(f"{API_BASE_URL}/baskets/").json()
        user_baskets = [b for b in all_baskets if b.get("user", {}).get("user_id") == message.from_user.id]
        for b in user_baskets:
            requests.delete(f"{API_BASE_URL}/baskets/{b.get('id')}/")

        amount = message.successful_payment.total_amount / 100

        success_text = (
            f"✅ Платеж успешно принят!\n"
            f"💰 Сумма: {amount:,.0f} сум\n"
            f"🎉 Ваш заказ оформлен!"
        ) if user_language == "ru" else (
            f"✅ To'lov qabul qilindi!\n"
            f"💰 Miqdor: {amount:,.0f} so'm\n"
            f"🎉 Buyurtmangiz ro'yxatdan o'tkazildi!"
        )

        # ❗ Inline tugmalarni shu yerga qo‘shamiz
        delivery_question = (
            "🏢 Mahsulotni ofisdan kelib olib ketasizmi yoki 📦 dostavka qilib yuboraylikmi?"
            if user_language == "uz"
            else "🏢 Заберёте товар из офиса или 📦 сделать доставку?"
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🏢 Ofisdan olib ketaman" if user_language == "uz" else "🏢 Заберу из офиса",
                        callback_data="pickup"
                    ),
                    InlineKeyboardButton(
                        text="📦 Dostavka qiling" if user_language == "uz" else "📦 Доставка",
                        callback_data="delivery"
                    )
                ]
            ]
        )
        await message.answer(success_text + "\n\n" + delivery_question, reply_markup=keyboard)

    except requests.exceptions.RequestException as e:
        print(f"❌ API so'rovida xatolik: {e}")
        error_msg = "❌ Ошибка при сохранении заказа." if user_language == "ru" else "❌ Buyurtmani saqlashda xatolik yuz berdi."
        await message.answer(error_msg)
    except Exception as e:
        print(f"❌ Umumiy xatolik: {str(e)}")
        error_msg = "❌ Произошла ошибка." if user_language == "ru" else "❌ Xatolik yuz berdi."
        await message.answer(error_msg)

@router.callback_query(F.data.in_(["pickup", "delivery"]))
async def handle_delivery_choice(callback: CallbackQuery, state: FSMContext):
    user_language = await get_user_language_from_state(state)

    if callback.data == "pickup":
        text = (
            "✅ Siz ofisdan olib ketishni tanladingiz.\n"
            "📞 Operatorlarimiz qisqa vaqtdan so‘ng siz bilan bog‘lanishadi."
            if user_language == "uz"
            else "✅ Вы выбрали самовывоз.\n📞 Наши операторы скоро с вами свяжутся."
        )
        await callback.message.answer(text)

    elif callback.data == "delivery":
        text = (
            "📍 Iltimos, joylashuvingizni (location) yuboring."
            if user_language == "uz"
            else "📍 Пожалуйста, отправьте свою локацию."
        )

        # Reply keyboard – Location yuborish tugmasi
        location_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📍 Location yuborish", request_location=True)]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )

        await callback.message.answer(text, reply_markup=location_keyboard)

@router.message(F.location)
async def get_user_location(message: Message, state: FSMContext):
    user_language = await get_user_language_from_state(state)

    latitude = message.location.latitude
    longitude = message.location.longitude

    # Kerak bo‘lsa backendga yuborish
    # requests.post(f"{API_BASE_URL}/save-location/", json={"lat": latitude, "lon": longitude, "user_id": message.from_user.id})

    text = (
        "✅ Location qabul qilindi!\n📞 Operatorlarimiz siz bilan bog‘lanishadi."
        if user_language == "uz"
        else "✅ Локация получена!\n📞 Наши операторы скоро с вами свяжутся."
    )
    await message.answer(text, reply_markup=None)