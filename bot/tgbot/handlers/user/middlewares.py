from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from create_bot import bot, config
from tgbot.handlers.user.inline import CheckChannelInline
from tgbot.api_models.redis_connector import RedisConnector as rds

module = "check_channel"
inline = CheckChannelInline(module=module)


class NotInChannelMiddleware(BaseMiddleware):

    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message | CallbackQuery,
                       data: Dict[str, Any]) -> Any:
        user_id = event.from_user.id
        text_handler = "subscribe_channel"
        user_channel_status = await bot.get_chat_member(chat_id=config.tg_bot.check_chat_id, user_id=user_id)
        if user_channel_status.status not in ["left", "kicked"]:
            return await handler(event, data)
        text = rds.get_user_text(user_id=user_id, module=module, handler=text_handler)
        kb = inline.chat_following_kb(user_id=user_id, handler=text_handler)
        await event.answer(text, reply_markup=kb)
