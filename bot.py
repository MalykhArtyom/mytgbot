import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import CommandStart
from dotenv import load_dotenv
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import get_last_requests, init_db, save_request, save_user

from db import init_db, save_request, save_user

load_dotenv()

proxy_url = os.getenv("PROXY_URL")
session = AiohttpSession(proxy=proxy_url) if proxy_url else None
bot = Bot(token=os.getenv("BOT_TOKEN"), session=session)
dp = Dispatcher()

from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

TEXTS = {
    "services": "Мои услуги:\n• Telegram-боты\n• Парсеры данных\n• Скрипты на Python",
    "prices": "Цены обсуждаются под задачу. Напишите, что нужно сделать.",
    "contact": "Связаться со мной: @fakzhresko",
    "test": "Тестовая функция"
}


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Услуги", callback_data="services"),
                InlineKeyboardButton(text="Цены", callback_data="prices")
            ],
            [
                InlineKeyboardButton(text="Связаться", callback_data="contact"),
                InlineKeyboardButton(text="Примеры работ", callback_data="test")
            ],
            [InlineKeyboardButton(text="Оставить заявку", callback_data="request")]
        ]
    )


def back_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="« Назад", callback_data="back")]]
    )


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    save_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    await message.answer("Привет! Выберите пункт:", reply_markup=main_menu())


@dp.callback_query(F.data.in_(TEXTS))
async def show_section(callback: CallbackQuery):
    await callback.message.edit_text(TEXTS[callback.data], reply_markup=back_button())
    await callback.answer()


@dp.callback_query(F.data == "back")
async def go_back(callback: CallbackQuery):
    await callback.message.edit_text("Выберите пункт:", reply_markup=main_menu())
    await callback.answer()

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

@dp.message(Command("requests"))
async def show_requests(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    rows = get_last_requests(10)
    if not rows:
        await message.answer("Заявок пока нет.")
        return

    lines = []
    for req_id, name, task, user_id, created_at in rows:
        lines.append(
            f"№{req_id} от {created_at}\n"
            f"Имя: {name}\n"
            f"Задача: {task}\n"
            f"ID: {user_id}"
        )
    await message.answer("\n\n".join(lines)[:4000])

class RequestForm(StatesGroup):
    name = State()
    task = State()

@dp.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено.", reply_markup=main_menu())

@dp.callback_query(F.data == "request")
async def request_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RequestForm.name)
    await callback.message.answer("Как к вам обращаться? (отмена: /cancel)")
    await callback.answer()


@dp.message(RequestForm.name, F.text)
async def request_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(RequestForm.task)
    await message.answer("Опишите задачу:")


@dp.message(RequestForm.task, F.text)
async def request_task(message: Message, state: FSMContext):
    data = await state.get_data()
    request_id = save_request(message.from_user.id, data["name"], message.text)
    await state.clear()
    await message.answer(
        f"Спасибо! Заявка №{request_id} принята, я свяжусь с вами.",
        reply_markup=main_menu(),
    )
    if ADMIN_ID:
        await bot.send_message(
            ADMIN_ID,
            f"Новая заявка №{request_id}\n"
            f"Имя: {data['name']}\n"
            f"Задача: {message.text}\n"
            f"От: @{message.from_user.username or message.from_user.id}",
        )


async def main():
    init_db()
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    me = await bot.get_me()
    print(f"Бот запущен: @{me.username}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())