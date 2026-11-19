import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from config import ADMIN_ID
from db import save_request
from keyboards import main_menu
from services import is_rate_limited, validate_name, validate_task

logger = logging.getLogger(__name__)
router = Router()


class RequestForm(StatesGroup):
    name = State()
    task = State()


@router.callback_query(F.data == "request")
async def request_start(callback: CallbackQuery, state: FSMContext):
    if is_rate_limited(callback.from_user.id):
        await callback.answer(
            "Вы отправили слишком много заявок. Попробуйте позже.", show_alert=True
        )
        return
    await state.set_state(RequestForm.name)
    await callback.message.answer("Как к вам обращаться? (отмена: /cancel)")
    await callback.answer()


@router.message(RequestForm.name, F.text, ~F.text.startswith("/"))
async def request_name(message: Message, state: FSMContext):
    name = message.text.strip()
    error = validate_name(name)
    if error:
        await message.answer(error)
        return
    await state.update_data(name=name)
    await state.set_state(RequestForm.task)
    await message.answer("Опишите задачу:")


@router.message(RequestForm.task, F.text, ~F.text.startswith("/"))
async def request_task(message: Message, state: FSMContext):
    task = message.text.strip()
    error = validate_task(task)
    if error:
        await message.answer(error)
        return

    data = await state.get_data()
    request_id = save_request(message.from_user.id, data["name"], task)
    await state.clear()
    await message.answer(
        f"Спасибо! Заявка №{request_id} принята, я свяжусь с вами.",
        reply_markup=main_menu(),
    )

    if ADMIN_ID:
        try:
            await message.bot.send_message(
                ADMIN_ID,
                f"Новая заявка №{request_id}\n"
                f"Имя: {data['name']}\n"
                f"Задача: {task}\n"
                f"От: @{message.from_user.username or message.from_user.id}",
            )
        except TelegramAPIError:
            logger.exception(
                "Не удалось отправить уведомление администратору (заявка №%s)", request_id
            )


@router.message(RequestForm.name)
@router.message(RequestForm.task)
async def request_not_text(message: Message):
    await message.answer("Пожалуйста, отправьте текстом (отмена: /cancel).")