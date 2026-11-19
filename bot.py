import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

from config import BOT_TOKEN, PROXY_URL
from db import init_db
from handlers import admin, menu, request_form


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler("bot.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    init_db()

    session = AiohttpSession(proxy=PROXY_URL) if PROXY_URL else None
    bot = Bot(token=BOT_TOKEN, session=session)
    dp = Dispatcher()

    # порядок важен: команды (/cancel) должны идти раньше формы
    dp.include_router(menu.router)
    dp.include_router(admin.router)
    dp.include_router(request_form.router)

    await bot.delete_webhook(drop_pending_updates=True)
    me = await bot.get_me()
    print(f"Бот запущен: @{me.username}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())