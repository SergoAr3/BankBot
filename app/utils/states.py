from aiogram.fsm.state import StatesGroup, State


class Transfer(StatesGroup):
    amount = State()
    username = State()
    confirm = State()


class Credit(StatesGroup):
    deadline = State()
    amount_1 = State()
    amount_2 = State()
    confirm = State()
    info = State()
    repay = State()
    repay_confirm = State()


class Deposit(StatesGroup):
    deadline = State()
    amount = State()
    confirm = State()
    info = State()
    withdraw = State()
    withdraw_confirm = State()