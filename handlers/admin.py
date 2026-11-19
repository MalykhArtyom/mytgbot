from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from config import ADMIN_ID
from db import get_last_requests

router = Router()
router.message.filter(F.from_user.id == ADMIN_ID)


@router.message(Command("requests"))
async def show_requests(message: Message):
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