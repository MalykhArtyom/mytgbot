from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from db import save_user
from keyboards import back_button, main_menu
from texts import TEXTS

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    save_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    await message.answer("Привет! Выберите пункт:", reply_markup=main_menu())


@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено.", reply_markup=main_menu())


@router.callback_query(F.data.in_(TEXTS))
async def show_section(callback: CallbackQuery):
    await callback.message.edit_text(TEXTS[callback.data], reply_markup=back_button())
    await callback.answer()


@router.callback_query(F.data == "back")
async def go_back(callback: CallbackQuery):
    await callback.message.edit_text("Выберите пункт:", reply_markup=main_menu())
    await callback.answer()