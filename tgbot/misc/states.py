from aiogram.fsm.state import State, StatesGroup


class AdminFSM(StatesGroup):
    home = State()
    get_files = State()
    search_files = State()
    support = State()


class UserFSM(StatesGroup):
    home = State()
    support = State()
