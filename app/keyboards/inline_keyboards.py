from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def get_menu_button() -> InlineKeyboardMarkup:
    menu_button_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Главное меню 📖', callback_data='menu')

            ],

        ],
        resize_keyboard=True
    )

    return menu_button_kb


async def get_back_menu_button() -> InlineKeyboardButton:
    back_menu_kb = InlineKeyboardButton(text='Назад ⏪', callback_data='back')

    return back_menu_kb


async def get_cancel_button() -> InlineKeyboardMarkup:
    cancel_button_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Отмена ❌', callback_data='cancel')
            ],

        ],
        resize_keyboard=True
    )

    return cancel_button_kb


async def get_start_kb() -> InlineKeyboardMarkup:
    start_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Главное меню 📖', callback_data='menu')
            ],
            [
                InlineKeyboardButton(text='Каналы 📄', callback_data='channels')
            ],

        ],
        resize_keyboard=True
    )

    return start_kb


async def get_menu_kb() -> InlineKeyboardMarkup:
    menu_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Мой баланс 💸‍', callback_data='balance')
            ],
            [
                InlineKeyboardButton(text='Перевести монеты 🔄‍', callback_data='transfer')
            ],
            [
                InlineKeyboardButton(text='Купить котика 😸‍', callback_data='buy_cat')
            ],
            [
                InlineKeyboardButton(text='Кредит 💵', callback_data='credit')
            ],
            [
                InlineKeyboardButton(text='Вклад 📈', callback_data='deposit')
            ],
            [
                InlineKeyboardButton(text='Подписки на каналы ✅', callback_data='subscriptions')
            ],

        ],
        resize_keyboard=True
    )

    return menu_kb


def get_credit_kb():
    back_menu_button = get_back_menu_button()
    credit_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Взять кредит 💵', callback_data='take_credit')
            ],
            [
                InlineKeyboardButton(text='Мои кредиты 🔎', callback_data='credit_info')
            ],
            [
                back_menu_button
            ],

        ],
        resize_keyboard=True
    )

    return credit_kb


def get_deposit_kb():
    back_menu_button = get_back_menu_button()
    deposit_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Открыть вклад 📈', callback_data='take_credit')
            ],
            [
                InlineKeyboardButton(text='Мои вклады 🔎', callback_data='credit_info')
            ],
            [
                back_menu_button
            ],

        ],
        resize_keyboard=True
    )

    return deposit_kb


async def get_transfer_confirm_kb():
    confirm_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Подтвердить ✅', callback_data='confirm_transfer')
            ],
            [
                InlineKeyboardButton(text='Отмена ❌', callback_data='cancel_transfer')
            ],

        ],
        resize_keyboard=True
    )

    return confirm_kb


async def get_buy_cat_kb():
    confirm_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Подтвердить ✅', callback_data='confirm_buy_cat')
            ],
            [
                InlineKeyboardButton(text='Назад ⏪', callback_data='back')
            ],

        ],
        resize_keyboard=True
    )

    return confirm_kb