from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Услуги", callback_data="services"),
                InlineKeyboardButton(text="Цены", callback_data="prices"),
            ],
            [
                InlineKeyboardButton(text="Связаться", callback_data="contact"),
                InlineKeyboardButton(text="Примеры работ", callback_data="test"),
            ],
            [InlineKeyboardButton(text="Оставить заявку", callback_data="request")],
        ]
    )


def back_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="« Назад", callback_data="back")]]
    )