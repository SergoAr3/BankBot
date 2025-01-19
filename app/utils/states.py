from aiogram.fsm.state import StatesGroup, State

class Transfer(StatesGroup):
    amount = State()
    username = State()
    confirm = State()

# class Start(StatesGroup):
#     start = State()
#
#
# class SetReminder(StatesGroup):
#     set_time = State()
#
#
# class Choice(StatesGroup):
#     choice_first = State()
#     choice_second = State()
#
#
# class Invite(StatesGroup):
#     friend_nickname = State()
#
#
# class Payment(StatesGroup):
#     payment = State()
