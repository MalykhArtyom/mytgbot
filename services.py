from config import (
    ADMIN_ID,
    MAX_NAME,
    MAX_REQUESTS_PER_HOUR,
    MAX_TASK,
    MIN_TASK,
)
from db import count_recent_requests


def validate_name(name: str) -> str | None:
    """Возвращает текст ошибки или None, если имя подходит."""
    if not name or len(name) > MAX_NAME:
        return f"Имя должно быть от 1 до {MAX_NAME} символов. Попробуйте ещё раз:"
    return None


def validate_task(task: str) -> str | None:
    if len(task) < MIN_TASK or len(task) > MAX_TASK:
        return f"Описание должно быть от {MIN_TASK} до {MAX_TASK} символов. Попробуйте ещё раз:"
    return None


def is_rate_limited(user_id: int) -> bool:
    if user_id == ADMIN_ID:
        return False
    return count_recent_requests(user_id) >= MAX_REQUESTS_PER_HOUR