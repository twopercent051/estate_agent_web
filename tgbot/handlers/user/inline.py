from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class InlineKeyboard:

    def __init__(self):
        self._home_button = InlineKeyboardButton(text='🏡 Main Menu', callback_data='home')

    def home_kb(self):
        keyboard = [[self._home_button]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def support_kb():
        keyboard = [[InlineKeyboardButton(text="📞 Support", callback_data="support")]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def answer_kb(user_id: str | int):
        keyboard = [[InlineKeyboardButton(text="📞 Ответить", callback_data=f"support:{user_id}")]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
