from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class InlineKeyboard:

    def __init__(self):
        self._home_button = InlineKeyboardButton(text='🏡 Домой', callback_data='home')

    def home_kb(self):
        keyboard = [[self._home_button]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def main_menu_kb():
        keyboard = [
            [InlineKeyboardButton(text="📦 Загрузка файлов", callback_data="upload_files")],
            [InlineKeyboardButton(text="🔎 Поиск файлов", callback_data="search_files")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def delete_kb(file_id: int):
        keyboard = [[InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete:{file_id}")]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def answer_kb():
        keyboard = [[InlineKeyboardButton(text="📞 Answer", callback_data=f"support")]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
