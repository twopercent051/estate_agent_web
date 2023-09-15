from aiogram.fsm.state import State, StatesGroup


class AdminFSM(StatesGroup):
    home = State()
    get_files = State()
    search_files = State()
    support = State()
    edit_text = State()
    mailing = State()
    edit_images = State()


class UserFSM(StatesGroup):
    home = State()
    support = State()
