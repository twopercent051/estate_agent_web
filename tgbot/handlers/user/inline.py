from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class MainInline:

    def __init__(self):
        self._home_button = InlineKeyboardButton(text='🏡 Main Menu', callback_data='home')

    def home_kb(self):
        keyboard = [[self._home_button]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def main_menu_kb():
        keyboard = [
            [InlineKeyboardButton(text="📖 Selection of the brochure", callback_data="select_brochure")],
            [InlineKeyboardButton(text="💰 Price calculation", callback_data="price_calculation")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


class SelectBrochureInline(MainInline):

    @staticmethod
    def support_kb():
        keyboard = [[InlineKeyboardButton(text="📞 Support", callback_data="support")]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def answer_kb(user_id: str | int):
        keyboard = [[InlineKeyboardButton(text="📞 Ответить", callback_data=f"support:{user_id}")]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


class CalculationPriceInline(MainInline):

    def there_are_payments_kb(self):
        keyboard = [
            [
                InlineKeyboardButton(text="Yes", callback_data="payments_yes"),
                InlineKeyboardButton(text="No", callback_data="payments_no"),
            ],
            [self._home_button]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def break_payments_kb(self):
        keyboard = [
            [InlineKeyboardButton(text="Break payments", callback_data="payments_no")],
            [self._home_button]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


class CheckChannelInline(MainInline):

    @staticmethod
    def chat_following_kb():
        keyboard = [
            [
                InlineKeyboardButton(text="Subscribe to the channel", url="https://t.me/artashesgri"),
                InlineKeyboardButton(text="I signed up", callback_data="home"),
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
