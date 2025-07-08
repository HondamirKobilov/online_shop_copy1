from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile
from typing import Optional
from datetime import datetime
from aiogram.types import InputMediaPhoto

from PIL import Image
from io import BytesIO
import requests
from aiogram.types import FSInputFile

from Bot.config import DOMAIN_URL
from Bot.keyboards.reply import main_menu_keyboard, main_menu_keyboard_ru
from Bot.utils.api import get_category_id_by_slug, get_products, get_category_slug_by_id, get_product_colors, \
    get_product_sizes, get_user_by_id, add_to_basket, get_categories

router = Router()

# Language management functions
async def get_user_language(state: FSMContext, default: str = "uz") -> str:
    """Get user language from state"""
    data = await state.get_data()
    return data.get("language", default)

async def set_user_language(state: FSMContext, language: str):
    """Set user language in state"""
    await state.update_data(language=language)

# Generate quantity keyboard with language support
def generate_quantity_keyboard(product_id: int, quantity: int, price: int, category_slug: Optional[str] = None, language: str = "uz"):
    # Button texts in both languages
    texts = {
        "uz": {
            "decrease": "➖ Kamaytirish (50)",
            "quantity": f"🛒 {quantity} dona - {price*quantity:,} so'm",
            "increase": "➕ Ko'paytirish (50)",
            "add": "📥 Savatga qo'shish",
            "back": "🔙 Orqaga",
            "upload": "🖼 Rasm qo'shish"
        },
        "ru": {
            "decrease": "➖ Уменьшить (50)",
            "quantity": f"🛒 {quantity} шт - {price*quantity:,} сум",
            "increase": "➕ Увеличить (50)",
            "add": "📥 В корзину",
            "back": "🔙 Назад",
            "upload": "🖼 Добавить фото"
        }
    }[language]

    keyboard = [
        [
            InlineKeyboardButton(text=texts["decrease"], callback_data=f"decrease_{product_id}"),
            InlineKeyboardButton(text=texts["increase"], callback_data=f"increase_{product_id}")
        ],
        [InlineKeyboardButton(text=texts["quantity"], callback_data="quantity_info")],
        [InlineKeyboardButton(text=texts["add"], callback_data=f"addbasket_{product_id}")],
        [InlineKeyboardButton(text=texts["upload"], callback_data=f"uploadphoto_{product_id}")]
    ]

    if category_slug:
        keyboard.append([InlineKeyboardButton(text=texts["back"], callback_data=f"category_{category_slug}")])
    else:
        keyboard.append([InlineKeyboardButton(text=texts["back"], callback_data="back_to_category_menu")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Main menu handlers
@router.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main_menu(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await callback.message.delete()
    user_language = await get_user_language(state)
    
    if user_language == "ru":
        await bot.send_message(
            chat_id=callback.from_user.id,
            text="🏠 Главное меню:",
            reply_markup=main_menu_keyboard_ru()
        )
    else:
        await bot.send_message(
            chat_id=callback.from_user.id,
            text="🏠 Bosh menyu:",
            reply_markup=main_menu_keyboard()
        )

@router.callback_query(lambda c: c.data == "back_to_category_menu")
async def back_to_category_menu(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    user_language = await get_user_language(state)

    categories = get_categories()
    if not categories:
        await call.message.answer("❌ Категории не найдены." if user_language == "ru" else "❌ Kategoriyalar topilmadi.")
        return

    keyboard = []
    row = []
    for i, cat in enumerate(categories, 1):
        row.append(InlineKeyboardButton(
            text=cat['name_ru'] if user_language == "ru" else cat['name'],
            callback_data=f"category_{cat['slug']}"
        ))
        if i % 2 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    image_url = FSInputFile("app/handlers/1.jpg")

    await call.message.answer_photo(
        photo=image_url,
        caption="🛍 Выберите категорию товаров:" if user_language == "ru" else "🛍 Mahsulot kategoriyalaridan birini tanlang:",
        reply_markup=markup
    )

# Products and categories handlers
@router.message(lambda msg: msg.text in ["🛍 Продукты", "🛍 Mahsulotlar"])
async def show_categories(msg: Message, state: FSMContext):
    # Set language based on which button was pressed
    user_language = "ru" if msg.text == "🛍 Продукты" else "uz"
    await set_user_language(state, user_language)
    categories = get_categories()
    if not categories:
        await msg.answer("❌ Категории не найдены." if user_language == "ru" else "❌ Kategoriyalar topilmadi.")
        return

    keyboard = []
    row = []
    for i, cat in enumerate(categories, 1):
        row.append(InlineKeyboardButton(
            text=cat['name_ru'] if user_language == "ru" else cat['name'],
            callback_data=f"category_{cat['slug']}"
        ))
        if i % 2 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    image_url = FSInputFile("app/handlers/1.jpg")

    await msg.answer_photo(
        photo=image_url,
        caption="🛍 Выберите категорию товаров:" if user_language == "ru" else "🛍 Mahsulot kategoriyalaridan birini tanlang:",
        reply_markup=markup
    )

@router.callback_query(F.data.startswith("category_"))
async def category_selected(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    user_language = await get_user_language(state)
    
    slug = call.data.replace("category_", "")
    category_id = get_category_id_by_slug(slug)
    if not category_id:
        await call.message.answer("❌ Категория не найдена." if user_language == "ru" else "❌ Kategoriya topilmadi.")
        return

    products = get_products()
    filtered = [p for p in products if p["category"] == category_id]

    if not filtered:
        await call.message.answer("📦 Товары в этой категории не найдены." if user_language == "ru" else "📦 Bu kategoriya uchun mahsulotlar topilmadi.")
        return

    keyboard = []
    row = []
    for i, p in enumerate(filtered, 1):
        row.append(InlineKeyboardButton(
            text=p['product_name_ru'] if user_language == "ru" else p['product_name'],
            callback_data=f"product_{p['id']}"
        ))
        if i % 2 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    # Back button
    keyboard.append([
        InlineKeyboardButton(
            text="🔙 Назад" if user_language == "ru" else "🔙 Orqaga", 
            callback_data="back_to_category_menu"
        )
    ])

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    image_url = FSInputFile("app/handlers/1.jpg")

    await call.message.answer_photo(
        photo=image_url,
        caption=f"📦 Товары в категории <b>{slug.title()}</b>:" if user_language == "ru" else f"📦 <b>{slug.title()}</b> uchun mahsulotlar:",
        reply_markup=markup
    )

@router.callback_query(F.data.startswith("product_"))
async def product_detail(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    user_language = await get_user_language(state)

    product_id = int(call.data.replace("product_", ""))
    product = next((p for p in get_products() if p["id"] == product_id), None)
    if not product:
        await call.message.answer("❌ Товар не найден." if user_language == "ru" else "❌ Mahsulot topilmadi.")
        return

    category_id = product["category"]
    category_slug = get_category_slug_by_id(category_id) or "unknown"

    quantity = 50
    await state.update_data(product_id=product_id, quantity=quantity)

    description = product.get('description_ru', product['description']) if user_language == "ru" else product['description']
    product_name = product.get('product_name_ru', product['product_name']) if user_language == "ru" else product['product_name']
    
    caption = (
        f"<b>{product_name}</b>\n\n"
        f"💵 Цена: {product['price']:,} сум\n" if user_language == "ru" else f"💵 Narxi: {product['price']:,} so'm\n"
        f"📝 Описание: {description}" if user_language == "ru" else f"📝 Tavsif: {description}"
    )

    # Barcha mavjud rasmlarni yig'amiz
    photo_urls = []
    for photo_field in ['photo', 'photo_2', 'photo_3']:
        if product.get(photo_field):
            photo_url = product[photo_field].replace("http://127.0.0.1:8000", DOMAIN_URL)\
                                          .replace("http://localhost:8000", DOMAIN_URL)\
                                          .replace("http://", "https://")
            photo_urls.append(photo_url)

    markup = generate_quantity_keyboard(product_id, quantity, product["price"], category_slug, user_language)

    try:
        if not photo_urls:
            # Agar rasm bo'lmasa, faqat tekst va tugmalar
            await call.message.answer(
                text=caption,
                reply_markup=markup
            )
        elif len(photo_urls) == 1:
            # Agar 1 ta rasm bo'lsa, oddiy photo + caption + reply_markup
            await call.message.answer_photo(
                photo=photo_urls[0],
                caption=caption,
                reply_markup=markup
            )
        else:
            # Agar ko'p rasim bo'lsa, media group + alohida xabar
            media_group = []
            for i, url in enumerate(photo_urls):
                if i == 0:  # Birinchi rasmga caption qo'shamiz
                    media_group.append(InputMediaPhoto(media=url, caption=caption))
                else:
                    media_group.append(InputMediaPhoto(media=url))
            
            # Media groupni yuborish
            await call.message.answer_media_group(media=media_group)
            
            # Tugmalarni alohida yuborish (agar media groupda caption bo'lsa ham, reply_markup ishlamaydi)
            await call.message.answer(
                text="👇 Quyidagi tugmalardan foydalaning" if user_language == "ru" else "👇 Quyidagi tugmalardan foydalaning",
                reply_markup=markup
            )

    except Exception as e:
        print(f"Rasmlarni yuborishda xatolik: {e}")
        # Agar xatolik bo'lsa, oddiy usulda yuborish
        await call.message.answer(
            text=caption,
            reply_markup=markup
        )

    colors = get_product_colors(product_id)
    sizes = get_product_sizes(product_id)
    await state.update_data(
        product_id=product_id,
        quantity=quantity,
        color_required=bool(colors),
        size_required=bool(sizes),
        product_photos=photo_urls
    )

@router.callback_query(F.data.startswith("color_"))
async def color_selected(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    user_language = await get_user_language(state)
@router.callback_query(F.data.startswith("color_"))
async def color_selected(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    user_language = await get_user_language(state)

    color_id = int(call.data.replace("color_", ""))
    await state.update_data(color_id=color_id)

    data = await state.get_data()
    product_id = data.get("product_id")
    product = next((p for p in get_products() if p["id"] == product_id), None)

    if not product:
        await call.message.answer("❌ Товар не найден." if user_language == "ru" else "❌ Mahsulot topilmadi.")
        return

    sizes = get_product_sizes(product_id)

    description = product['description_ru'] if user_language == "ru" else product['description']
    product_name = product['product_name_ru'] if user_language == "ru" else product['product_name']
    
    caption = (
        f"<b>{product_name}</b>\n\n"
        f"💵 Цена: {product['price']:,} сум\n" if user_language == "ru" else f"💵 Narxi: {product['price']:,} so'm\n"
        f"📝 Описание: {description}" if user_language == "ru" else f"📝 Tavsif: {description}"
    )
    photo_url = product["photo"].replace("http://127.0.0.1:8000", DOMAIN_URL).replace("http://", "https://")

    if sizes:
        size_buttons = [
            InlineKeyboardButton(
                text=size["name_ru"] if user_language == "ru" and "name_ru" in size else size["name"], 
                callback_data=f"size_{size['id']}"
            )
            for size in sizes
        ]
        size_keyboard = [size_buttons[i:i + 2] for i in range(0, len(size_buttons), 2)]
        markup = InlineKeyboardMarkup(inline_keyboard=size_keyboard)

        await call.message.answer_photo(
            photo=photo_url,
            caption=caption + "\n\n📏 Пожалуйста, выберите <b>размер</b> товара:" if user_language == "ru" else "\n\n📏 Iltimos, mahsulot uchun <b>razmer</b> tanlang:",
            reply_markup=markup
        )
    else:
        quantity = data.get("quantity", 50)
        keyboard = generate_quantity_keyboard(product_id, quantity, product["price"], language=user_language)
        await call.message.answer_photo(
            photo=photo_url,
            caption=caption,
            reply_markup=keyboard
        )

@router.callback_query(F.data.startswith("size_"))
async def size_selected(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    user_language = await get_user_language(state)

    size_id = int(call.data.replace("size_", ""))
    await state.update_data(size_id=size_id)

    data = await state.get_data()
    product_id = data.get("product_id")
    quantity = data.get("quantity", 50)

    user = get_user_by_id(call.from_user.id)
    if not user:
        await call.message.answer("❌ Пользователь не найден." if user_language == "ru" else "❌ Foydalanuvchi topilmadi.")
        return

    user_pk = user["id"]

    success = add_to_basket(
        user_id=user_pk,
        product_id=product_id,
        number=quantity,
        color_id=data.get("color_id"),
        size_id=size_id
    )

    if success:
        await call.message.answer("✅ Товар добавлен в корзину!" if user_language == "ru" else "✅ Mahsulot savatga qo'shildi!")
        await state.clear()
    else:
        await call.message.answer("❌ Ошибка: Вы уже добавили этот товар в корзину." if user_language == "ru" else "❌ Xatolik: Siz bu mahsulotni allaqachon savatga qo'shgansiz.")

# Quantity adjustment handlers
@router.callback_query(F.data.startswith("increase_"))
async def increase_quantity(call: CallbackQuery, state: FSMContext):
    user_language = await get_user_language(state)
    data = await state.get_data()
    quantity = data.get("quantity", 50)
    quantity += 50
    product_id = int(call.data.replace("increase_", ""))
    await state.update_data(quantity=quantity)

    product = next((p for p in get_products() if p["id"] == product_id), None)
    if product:
        category_slug = get_category_slug_by_id(product["category"]) or "unknown"

        await call.message.edit_reply_markup(
            reply_markup=generate_quantity_keyboard(
                product_id, 
                quantity, 
                product["price"], 
                category_slug,
                user_language
            )
        )

@router.callback_query(F.data.startswith("decrease_"))
async def decrease_quantity(call: CallbackQuery, state: FSMContext):
    user_language = await get_user_language(state)
    data = await state.get_data()
    quantity = data.get("quantity", 50)
    if quantity <= 50:
        await call.answer(
            "❗️Минимальное количество - 50!" if user_language == "ru" else "❗️Eng kamida 50 dona bo'lishi kerak!", 
            show_alert=True
        )
        return

    quantity -= 50
    product_id = int(call.data.replace("decrease_", ""))
    await state.update_data(quantity=quantity)

    product = next((p for p in get_products() if p["id"] == product_id), None)
    if product:
        category_slug = get_category_slug_by_id(product["category"]) or "unknown"

        await call.message.edit_reply_markup(
            reply_markup=generate_quantity_keyboard(
                product_id, 
                quantity, 
                product["price"], 
                category_slug,
                user_language
            )
        )

# Add to basket handler
@router.callback_query(F.data.startswith("addbasket_"))
async def add_to_cart(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    user_language = await get_user_language(state)

    data = await state.get_data()
    quantity = data.get("quantity", 50)
    product_id = int(call.data.replace("addbasket_", ""))

    color_id = data.get("color_id")
    size_id = data.get("size_id")

    product = next((p for p in get_products() if p["id"] == product_id), None)
    if not product:
        await call.message.answer("❌ Товар не найден." if user_language == "ru" else "❌ Mahsulot topilmadi.")
        return

    colors = get_product_colors(product_id)
    sizes = get_product_sizes(product_id)

    description = product['description_ru'] if user_language == "ru" else product['description']
    product_name = product['product_name_ru'] if user_language == "ru" else product['product_name']
    
    caption = (
        f"<b>{product_name}</b>\n\n"
        f"💵 Цена: {product['price']:,} сум\n" if user_language == "ru" else f"💵 Narxi: {product['price']:,} so'm\n"
        f"📝 Описание: {description}" if user_language == "ru" else f"📝 Tavsif: {description}"
    )
    photo_url = product["photo"].replace("http://127.0.0.1:8000", DOMAIN_URL).replace("http://localhost:8000", DOMAIN_URL).replace("http://", "https://")

    if colors and not color_id:
        color_buttons = [
            InlineKeyboardButton(
                text=color["name_ru"] if user_language == "ru" and "name_ru" in color else color["name"], 
                callback_data=f"color_{color['id']}"
            )
            for color in colors
        ]
        color_keyboard = [color_buttons[i:i + 2] for i in range(0, len(color_buttons), 2)]
        markup = InlineKeyboardMarkup(inline_keyboard=color_keyboard)

        await call.message.answer_photo(
            photo=photo_url, 
            caption=caption + "\n\n🎨 Пожалуйста, выберите <b>цвет</b> товара:" if user_language == "ru" else "\n\n🎨 Iltimos, mahsulot uchun <b>rang</b> tanlang:",
            reply_markup=markup
        )
        return

    if sizes and not size_id:
        size_buttons = [
            InlineKeyboardButton(
                text=size["name_ru"] if user_language == "ru" and "name_ru" in size else size["name"], 
                callback_data=f"size_{size['id']}"
            )
            for size in sizes
        ]
        size_keyboard = [size_buttons[i:i + 2] for i in range(0, len(size_buttons), 2)]
        markup = InlineKeyboardMarkup(inline_keyboard=size_keyboard)

        await call.message.answer_photo(
            photo=photo_url,
            caption=caption + "\n\n📏 Пожалуйста, выберите <b>размер</b> товара:" if user_language == "ru" else "\n\n📏 Iltimos, mahsulot uchun <b>razmer</b> tanlang:",
            reply_markup=markup
        )
        return

    user = get_user_by_id(call.from_user.id)
    if not user:
        await call.message.answer("❌ Пользователь не найден." if user_language == "ru" else "❌ Foydalanuvchi topilmadi.")
        return

    payload = {
        "user_id": user["id"],
        "product_id": product_id,
        "number": quantity
    }
    if color_id:
        payload["color_id"] = color_id
    if size_id:
        payload["size_id"] = size_id

    if add_to_basket(**payload):
        await call.message.answer("✅ Товар добавлен в корзину!" if user_language == "ru" else "✅ Mahsulot savatga qo'shildi!")
        await state.clear()
    else:
        await call.message.answer("❌ Ошибка: Вы уже добавили этот товар в корзину." if user_language == "ru" else "❌ Xatolik: Siz bu mahsulotni allaqachon savatga qo'shgansiz.")

# Photo upload handlers
@router.callback_query(F.data.startswith("uploadphoto_"))
async def request_user_photo(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    user_language = await get_user_language(state)
    
    product_id = int(call.data.replace("uploadphoto_", ""))
    await state.update_data(waiting_photo=True, product_id=product_id)
    await call.message.answer("📸 Отправьте фото. Оно будет добавлено к изображению товара." if user_language == "ru" else "📸 Rasm yuboring. U mahsulot rasmingizga qo'shiladi.")

@router.message(F.photo | F.document)
async def handle_user_photo(msg: Message, state: FSMContext, bot: Bot):
    user_language = await get_user_language(state)
    data = await state.get_data()
    
    if not data.get("waiting_photo"):
        return

    processing_msg = await msg.answer("⏳ Обработка изображения..." if user_language == "ru" else "⏳ Rasmga ishlov berilmoqda...")

    product_id = data.get("product_id")
    product = next((p for p in get_products() if p["id"] == product_id), None)
    if not product:
        await msg.answer("❌ Товар не найден." if user_language == "ru" else "❌ Mahsulot topilmadi.")
        return

    try:
        if msg.photo:
            tg_file = await bot.get_file(msg.photo[-1].file_id)
        elif msg.document and msg.document.mime_type.startswith("image/"):
            tg_file = await bot.get_file(msg.document.file_id)
        else:
            await msg.answer("❌ Пожалуйста, отправьте только изображение." if user_language == "ru" else "❌ Iltimos, faqat rasm faylini yuboring.")
            return

        photo_file = BytesIO()
        await bot.download_file(tg_file.file_path, destination=photo_file)
        photo_file.seek(0)
        user_img = Image.open(photo_file).convert("RGBA").resize((150, 100))

        product_url = product['photo'].replace("http://127.0.0.1:8000", DOMAIN_URL)
        resp = requests.get(product_url)
        if resp.status_code != 200:
            await msg.answer("❌ Не удалось получить изображение товара." if user_language == "ru" else "❌ Mahsulot rasmi olinmadi.")
            return
        product_img = Image.open(BytesIO(resp.content)).convert("RGBA")

        pw, ph = product_img.size
        px = (pw - 150) // 2
        py = (ph - 10) // 2
        product_img.paste(user_img, (px, py), user_img)

        out = BytesIO()
        product_img.save(out, format="PNG")
        out.seek(0)

        filename = f"combined_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        photo_input = BufferedInputFile(file=out.read(), filename=filename)

        await bot.delete_message(chat_id=msg.chat.id, message_id=processing_msg.message_id)
        await msg.answer_photo(
            photo=photo_input, 
            caption="✅ Ваше изображение добавлено к товару!" if user_language == "ru" else "✅ Sizning rasmingiz mahsulotga joylandi!"
        )

    except Exception as e:
        await msg.answer("❌ Произошла ошибка при обработке." if user_language == "ru" else "❌ Ishlov berishda xatolik yuz berdi.")
        print("Error:", e)

    await state.clear()