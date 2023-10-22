from typing import Optional

from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext

from create_bot import bot, config
from tgbot.misc.states import UserFSM
from tgbot.models.redis_connector import RedisConnector
from tgbot.models.sql_connector import UsersDAO
from tgbot.handlers.user.inline import MainInline

router = Router()
module = "main_block"
inline = MainInline(module=module)

admin_group = config.tg_bot.admin_group
rds = RedisConnector()


async def start_render(user_id: str | int, username: Optional[str]):
    handler = "main_menu"
    username = f"@{username}" if username else "---"
    current_user = await UsersDAO.get_one_or_none(user_id=str(user_id))
    if not current_user:
        await UsersDAO.create(user_id=str(user_id), username=username)
    text = rds.get_user_text(user_id=user_id, module=module, handler=handler)
    kb = inline.main_menu_kb(user_id=user_id, handler=handler)
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb)


@router.message(Command("start"))
async def main_block(message: Message, state: FSMContext):
    await start_render(user_id=message.from_user.id, username=message.from_user.username)
    await state.set_state(UserFSM.home)


@router.callback_query(F.data == "home")
async def main_block(callback: CallbackQuery, state: FSMContext):
    await start_render(user_id=callback.from_user.id, username=callback.from_user.username)
    await state.set_state(UserFSM.home)
    await bot.answer_callback_query(callback.id)
