from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

import app.constans.deadlines as dl
import app.constans.messages as msg


async def get_choice_deadline_kb() -> ReplyKeyboardMarkup:
    choice_deadline_kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=dl.DEADLINE_1_MESSAGE, )
            ],
            [
                KeyboardButton(text=dl.DEADLINE_2_MESSAGE)
            ],
            [
                KeyboardButton(text=msg.CANCEL_BUTTON_MESSAGE)
            ],

        ],
        resize_keyboard=True
    )

    return choice_deadline_kb


async def get_choice_amount_kb_1() -> ReplyKeyboardMarkup:
    choice_amount_kb_1 = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='10')
            ],
            [
                KeyboardButton(text='100')
            ],
            [
                KeyboardButton(text='1000')
            ],
            [
                KeyboardButton(text=msg.CANCEL_BUTTON_MESSAGE)
            ],

        ],
        resize_keyboard=True
    )

    return choice_amount_kb_1


async def get_choice_amount_kb_2() -> ReplyKeyboardMarkup:
    choice_amount_kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='100')
            ],
            [
                KeyboardButton(text='500')
            ],
            [
                KeyboardButton(text='5000')
            ],
            [
                KeyboardButton(text=msg.CANCEL_BUTTON_MESSAGE)
            ],

        ],
        resize_keyboard=True
    )

    return choice_amount_kb
