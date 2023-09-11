from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from create_bot import bot, config
from tgbot.handlers.user.inline import InlineKeyboard
from tgbot.models.sql_connector import TextsDAO

inline = InlineKeyboard()


class NotInChannelMiddleware(BaseMiddleware):

    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message | CallbackQuery,
                       data: Dict[str, Any]) -> Any:
        user_channel_status = await bot.get_chat_member(chat_id=config.tg_bot.check_chat_id, user_id=event.from_user.id)
        if user_channel_status.status not in ["left", "kicked"]:
            return await handler(event, data)
        text = await TextsDAO.get_text(chapter="subscribe_channel")
        kb = inline.chat_following_kb()
        await event.answer(text, reply_markup=kb)