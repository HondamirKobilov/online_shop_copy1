from aiogram import Router
from aiogram.types import Message

from Bot.utils.api import get_contact_text, get_social_links

router = Router()

# 📞 Bog'lanish
@router.message(lambda msg: msg.text in ["📞 Bog'lanish", "📞 Связь"])
async def contact_handler(msg: Message):
    contact_info = get_contact_text()
    await msg.answer(f"📞 <b>Bog‘lanish uchun ma’lumot:\n\n📞 Контактная информация:</b>\n\n{contact_info}")

# 🔵 Ijtimoiy tarmoq
@router.message(lambda msg: msg.text in ["🔵 Ijtimoiy tarmoq","🔵 Социальная сеть"])
async def social_links_handler(msg: Message):
    text, markup = get_social_links()
    await msg.answer(text, reply_markup=markup, disable_web_page_preview=True)
