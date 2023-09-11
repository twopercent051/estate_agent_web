import itertools
from typing import Optional

from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext

from create_bot import bot, config
from tgbot.misc.states import UserFSM
from tgbot.models.sql_connector import FilesDAO, TextsDAO, UsersDAO
from .inline import InlineKeyboard
from .middlewares import NotInChannelMiddleware

router = Router()
router.message.outer_middleware(NotInChannelMiddleware())
router.callback_query.outer_middleware(NotInChannelMiddleware())

inline = InlineKeyboard()

admin_group = config.tg_bot.admin_group


async def start_render(user_id: str | int, username: Optional[str]):
    username = f"@{username}" if username else "---"
    try:
        await UsersDAO.create(user_id=str(user_id), username=username)
    except:
        pass
    text = await TextsDAO.get_text(chapter="greeting")
    await bot.send_message(chat_id=user_id, text=text)


@router.message(Command("start"))
async def main_block(message: Message, state: FSMContext):
    await start_render(user_id=message.from_user.id, username=message.from_user.username)
    await state.set_state(UserFSM.home)


@router.callback_query(F.data == "home")
async def main_block(callback: CallbackQuery, state: FSMContext):
    await start_render(user_id=callback.from_user.id, username=callback.from_user.username)
    await state.set_state(UserFSM.home)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, UserFSM.home)
async def main_block(message: Message):
    keyword = message.text.lower().replace("_", " ")
    files = await FilesDAO.get_many_by_keyword(keyword=keyword)
    await UsersDAO.update_requests(user_id=str(message.from_user.id))
    kb = inline.support_kb()
    if len(files) == 0:
        text = await TextsDAO.get_text(chapter="nothing_found")
        await message.answer(text, reply_markup=kb)
    elif len(files) == 1:
        await message.answer_document(document=files[0]["file_id"], reply_markup=kb)
    else:
        it = iter(files[:50])
        chunks = iter(lambda: tuple(itertools.islice(it, 10)), ())
        for chunk in chunks:
            media_group = []
            for file in chunk:
                media_group.append(dict(media=file["file_id"], type="document"))
                await message.answer_media_group(media_group)
        text = await TextsDAO.get_text(chapter="found_materials")
        await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "support")
async def main_block(callback: CallbackQuery, state: FSMContext):
    text = await TextsDAO.get_text(chapter="write_request")
    kb = inline.home_kb()
    await state.set_state(UserFSM.support)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, UserFSM.support)
@router.message(F.photo, UserFSM.support)
@router.message(F.document, UserFSM.support)
async def main_block(message: Message, state: FSMContext):
    username = f"@{message.from_user.username}" if message.from_user.username else "---"
    kb = inline.answer_kb(user_id=message.from_user.id)
    text = f"⚠️ Сообщение от пользователя {username}:\n\n{message.text}"
    if message.content_type == "text":
        await bot.send_message(chat_id=admin_group, text=text, reply_markup=kb)
    if message.content_type == "photo":
        photo_id = message.photo[-1].file_id
        await bot.send_photo(chat_id=admin_group, photo=photo_id, caption=text, reply_markup=kb)
    if message.content_type == "document":
        document_id = message.document.file_id
        await bot.send_document(chat_id=admin_group, document=document_id, caption=text, reply_markup=kb)
    text = await TextsDAO.get_text(chapter="message_sent")
    kb = inline.home_kb()
    await state.set_state(UserFSM.home)
    await message.answer(text, reply_markup=kb)
