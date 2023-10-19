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
    search_brochure = State()
    support = State()
    net_to_seller = State()
    payment_date = State()
    payment_value = State()
    proposal_title = State()
    album_photo = State()
    layout_photo = State()
    description = State()
    calc_photo = State()
