import logging
import requests
from Bot.config import API_BASE_URL

def check_user_exists(user_id):
    try:
        res = requests.get(f"{API_BASE_URL}/users/", params={"user_id": user_id})
        if res.status_code == 200:
            return any(u["user_id"] == user_id for u in res.json())
    except:
        pass
    return False

def register_user(data):
    try:
        res = requests.post(f"{API_BASE_URL}/users/", json=data)
        return res.status_code == 201
    except:
        return False

def get_contact_text():
    try:
        res = requests.get(f"{API_BASE_URL}/contact/")
        if res.status_code == 200 and len(res.json()) > 0:
            return res.json()[0]["text"]
    except:
        pass
    return "📞 Hozircha bog‘lanish ma’lumotlari mavjud emas."


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_social_links():
    try:
        res = requests.get(f"{API_BASE_URL}/social-media/")
        if res.status_code == 200:
            data = res.json()
            if not data:
                return "📵 Ijtimoiy tarmoqlar ro'yxati topilmadi.", None

            text = "<b>🔗 Bizning ijtimoiy tarmoqlar:\n\n🔗 Наши социальные сети:</b>"
            buttons = []
            for item in data:
                name = item.get("name", "Tarmoq")
                url = item.get("url", "#")
                buttons.append([InlineKeyboardButton(text=name, url=url)])

            markup = InlineKeyboardMarkup(inline_keyboard=buttons)
            return text, markup
    except:
        pass
    return "❌ Ijtimoiy tarmoqlarni yuklashda xatolik yuz berdi.", None


def get_user_by_id(user_id):
    try:
        res = requests.get(f"{API_BASE_URL}/users/", params={"user_id": user_id})
        if res.status_code == 200:
            users = res.json()
            for u in users:
                if u["user_id"] == user_id:
                    return u
    except:
        pass
    return None

def update_user_field(user_id, field, value):
    try:
        # PATCH uchun user ID (model ID, emas telegram user_id) kerak bo'ladi
        all_users = requests.get(f"{API_BASE_URL}/users/").json()
        target = next((u for u in all_users if u["user_id"] == user_id), None)
        if not target:
            return False
        res = requests.patch(f"{API_BASE_URL}/users/{target['id']}/", json={field: value})
        return res.status_code in [200, 202]
    except:
        return False

def get_categories():
    try:
        res = requests.get(f"{API_BASE_URL}/categories/")
        if res.status_code == 200:
            return res.json()
    except:
        pass
        print("xatolik categoriy abosh")
    return []

def get_products():
    try:
        res = requests.get(f"{API_BASE_URL}/products/")
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return []

def get_category_id_by_slug(slug):
    categories = get_categories()
    for cat in categories:
        if cat["slug"] == slug:
            return cat["id"]
    return None

def get_user_model_id(telegram_user_id):
    """Telegram user_id bo‘yicha model id ni qaytaradi (user_id → id)"""
    try:
        res = requests.get(f"{API_BASE_URL}/users/", params={"user_id": telegram_user_id})
        if res.status_code == 200:
            users = res.json()
            user = next((u for u in users if u["user_id"] == telegram_user_id), None)
            if user:
                return user["id"]
    except:
        pass
    return None

logger = logging.getLogger(__name__)

def add_to_basket(user_id, product_id, number, color_id=None, size_id=None):
    response = requests.post(f"{API_BASE_URL}/baskets/", json={
        "user_id": user_id,
        "product_id": product_id,
        "number": number,
        "color_id": color_id,
        "size_id": size_id
    })

    print("➡️ POST:", response.request.body)
    print("⬅️ RESPONSE:", response.status_code, response.text)

    if response.status_code == 201:
        return True
    return False


def get_product_colors(product_id):
    try:
        res = requests.get(f"{API_BASE_URL}/products/{product_id}/")
        if res.status_code == 200:
            product = res.json()
            return product.get("colors", [])
    except:
        pass
    return []

def get_product_sizes(product_id):
    try:
        res = requests.get(f"{API_BASE_URL}/products/{product_id}/")
        if res.status_code == 200:
            product = res.json()
            return product.get("sizes", [])
    except:
        pass
    return []

def get_category_slug_by_id(category_id):
    categories = get_categories()
    for cat in categories:
        if cat["id"] == category_id:
            return cat["slug"]
    return None
