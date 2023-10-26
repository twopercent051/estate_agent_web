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
            # [InlineKeyboardButton(text="📝 Редактура текстов", callback_data="edit_texts")],
            [InlineKeyboardButton(text="🌅 Редактура альбома", callback_data="edit_images")],
            [InlineKeyboardButton(text="📈 Статистика", callback_data="statistics")],
            [InlineKeyboardButton(text="✉️ Рассылка", callback_data="mailing")],
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

    def edit_texts_kb(self):
        kb_dict = dict(subscribe_channel="Подпишитесь на канал",
                       main_menu="Главное меню",
                       greeting_select_brochure="Приветствие поиска брошюры",
                       nothing_found="Ничего не найдено",
                       found_materials="Найдены брошюры",
                       write_request="Напишите свой вопрос",
                       message_sent="Сообщение отправлено",
                       message_from_support="Сообщение от поддержки",
                       net_to_seller="Net to seller",
                       enter_date="Введите дату",
                       enter_payment="Введите платёж",
                       not_integer="Ввели не число",
                       there_are_payments="Есть ли платежи?",
                       continue_payments="Продолжить ввод платежей?",
                       calculation_result="Результат расчёта",
                       proposal_title="Название в телеграфе",
                       album_photo="Альбом фотографий",
                       is_more_photo="Еще фотографии?",
                       layout_photo="Фото планировки",
                       description="Описание",
                       calc_photo="Скрин расчёта",
                       proposal_result="Результат Телеграф")
        keyboard = []
        for button in kb_dict:
            keyboard.append([InlineKeyboardButton(text=kb_dict[button], callback_data=f"edit_text:{button}")])
        keyboard.append([self._home_button])
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
