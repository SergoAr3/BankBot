from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def get_menu_button_kb() -> InlineKeyboardMarkup:
    menu_button_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Главное меню 📖', callback_data='menu')

            ],

        ],
        resize_keyboard=True
    )

    return menu_button_kb


async def get_user_credit_info_kb(credit_id: int) -> InlineKeyboardMarkup:
    user_credit_info_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Погасить 💰', callback_data=f'repay_credit_{credit_id}')
            ],
            [
                InlineKeyboardButton(text='Назад ⏪', callback_data='back_active_user_credits')
            ],

        ],
        resize_keyboard=True
    )

    return user_credit_info_kb


async def get_user_deposit_info_kb(credit_id: int) -> InlineKeyboardMarkup:
    user_deposit_info_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Вывести монеты 💰', callback_data=f'withdraw_deposit_{credit_id}')
            ],
            [
                InlineKeyboardButton(text='Назад ⏪', callback_data='back_active_user_deposits')
            ],

        ],
        resize_keyboard=True
    )

    return user_deposit_info_kb


async def get_back_credit_menu_button_kb() -> InlineKeyboardMarkup:
    back_button_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Назад ⏪', callback_data='back_credit_menu')
            ],

        ],
        resize_keyboard=True
    )

    return back_button_kb


async def get_deposit_credit_menu_button_kb() -> InlineKeyboardMarkup:
    back_button_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Назад ⏪', callback_data='back_deposit_menu')
            ],

        ],
        resize_keyboard=True
    )

    return back_button_kb


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
                InlineKeyboardButton(text='Подписки на каналы ✅', callback_data='channels')
            ],

        ],
        resize_keyboard=True
    )

    return menu_kb


async def get_credit_kb():
    credit_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Взять кредит 💵', callback_data='take_credit')
            ],
            [
                InlineKeyboardButton(text='Мои кредиты 🔎', callback_data='credits_info')
            ],
            [
                InlineKeyboardButton(text='Назад ⏪', callback_data='back')
            ],

        ],
        resize_keyboard=True
    )

    return credit_kb


async def get_deposit_kb():
    deposit_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Открыть вклад 📈', callback_data='take_deposit')
            ],
            [
                InlineKeyboardButton(text='Мои вклады 🔎', callback_data='deposits_info')
            ],
            [
                InlineKeyboardButton(text='Назад ⏪', callback_data='back')
            ],

        ],
        resize_keyboard=True
    )

    return deposit_kb


async def get_confirm_kb(deal_type: str):
    confirm_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Подтвердить ✅', callback_data=f'confirm_{deal_type}')
            ],
            [
                InlineKeyboardButton(text='Отмена ❌', callback_data=f'cancel_{deal_type}')
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


async def get_check_subscriptions_button():
    confirm_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Проверить подписки ✔︎', callback_data='check_subscriptions')
            ]

        ],
        resize_keyboard=True
    )

    return confirm_kb


async def get_user_active_credits_kb(user_active_credits):
    inline_keyboard = [[InlineKeyboardButton(text=f'{rank}. Кредит на {credit.amount} монет',
                                             callback_data=f'active_credit_{credit.id}')]
                       for rank, credit in enumerate(user_active_credits, start=1)]
    inline_keyboard.append([InlineKeyboardButton(text='Назад ⏪', callback_data='back_credit_menu')])

    confirm_kb = InlineKeyboardMarkup(
        inline_keyboard=inline_keyboard,

        resize_keyboard=True
    )

    return confirm_kb


async def get_user_active_deposits_kb(user_active_deposits):
    inline_keyboard = [[InlineKeyboardButton(text=f'{rank}. Вклад на {deposit.amount} монет',
                                             callback_data=f'active_deposit_{deposit.id}')]
                       for rank, deposit in enumerate(user_active_deposits, start=1)]
    inline_keyboard.append([InlineKeyboardButton(text='Назад ⏪', callback_data='back_deposit_menu')])

    confirm_kb = InlineKeyboardMarkup(
        inline_keyboard=inline_keyboard,

        resize_keyboard=True
    )

    return confirm_kb


async def get_deposit_withdraw_kb() -> InlineKeyboardMarkup:
    cancel_button_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Продолжить ➡️', callback_data='continue_withdraw')
            ],
            [
                InlineKeyboardButton(text='Отмена ❌', callback_data='cancel')
            ],

        ],
        resize_keyboard=True
    )

    return cancel_button_kb
