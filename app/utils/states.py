from aiogram.fsm.state import StatesGroup, State

class Transfer(StatesGroup):
    amount = State()
    username = State()
    confirm = State()
