from aiogram.fsm.context import FSMContext
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import BOT_TOKEN
from handlers.start import router as start_router
from handlers.register import router as register_router
from handlers.menu import router as menu_router
from handlers.settings import router as settings_router
from handlers.basket_handlers import router as basket_router
from handlers.products import router as product_router
from handlers.my_orders import router as my_orders_router


async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start_router)
    dp.include_router(register_router)
    dp.include_router(menu_router)
    dp.include_router(settings_router)
    dp.include_router(basket_router)
    dp.include_router(product_router)
    dp.include_router(my_orders_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
