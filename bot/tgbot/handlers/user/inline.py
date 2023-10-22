from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.tgbot.models.redis_connector import RedisConnector


class MainInline:
    _rds = RedisConnector()

    def __init__(self, module: str):
        self._module = module

    def _create_button(self, user_id: str | int, handler: str, clb_data: str, is_home: bool = False):
        module = "main_block" if is_home else self._module
        return InlineKeyboardButton(text=self._rds.get_user_text(user_id=user_id,
                                                                 module=module,
                                                                 handler=handler,
                                                                 obj=clb_data), callback_data=clb_data)

    def _home_button(self, user_id: str | int):
        return self._create_button(user_id=user_id, handler="all", clb_data="home", is_home=True)

    def home_kb(self, user_id: str | int):
        keyboard = [[self._home_button(user_id=user_id)]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def main_menu_kb(self, user_id: int | str, handler: str):
        keyboard = [
            [self._create_button(user_id=user_id, handler=handler, clb_data="select_brochure")],
            [self._create_button(user_id=user_id, handler=handler, clb_data="price_calculation")],
            [self._create_button(user_id=user_id, handler=handler, clb_data="commercial_proposal")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


class SelectBrochureInline(MainInline):

    def support_kb(self, user_id: str | int, handler: str):
        keyboard = [[self._create_button(user_id=user_id, handler=handler, clb_data="support")]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def answer_user_kb(user_id: str | int):
        keyboard = [[InlineKeyboardButton(text="📞 Ответить", callback_data=f"support:{user_id}")]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def answer_admin_kb(self, user_id: str | int, handler: str):
        keyboard = [[self._create_button(user_id=user_id, handler=handler, clb_data="support")]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


class CalculationPriceInline(MainInline):

    def there_are_payments_kb(self, user_id: int | str, handler: str):
        keyboard = [
            [
                self._create_button(user_id=user_id, handler=handler, clb_data="payments_yes"),
                self._create_button(user_id=user_id, handler=handler, clb_data="payments_no"),
            ],
            [self._home_button]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def break_payments_kb(self, user_id: int | str, handler: str):
        keyboard = [
            [self._create_button(user_id=user_id, handler=handler, clb_data="payments_no")],
            [self._home_button]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


class CommercialProposalInline(MainInline):

    def upload_layout_photo_kb(self, user_id: int | str, handler: str):
        keyboard = [
            [
                self._create_button(user_id=user_id, handler=handler, clb_data="upload_layout"),
                self._home_button
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


class CheckChannelInline(MainInline):

    def chat_following_kb(self, user_id: int | str, handler: str):
        subscribe_text = self._rds.get_user_text(user_id=user_id, module=self._module, handler=handler, obj="subscribe")
        i_signed_up_text = self._rds.get_user_text(user_id=user_id,
                                                   module=self._module,
                                                   handler=handler,
                                                   obj="i_signed_up")
        keyboard = [
            [
                InlineKeyboardButton(text=subscribe_text, url="https://t.me/artashesgri"),
                InlineKeyboardButton(text=i_signed_up_text, callback_data="home"),
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
