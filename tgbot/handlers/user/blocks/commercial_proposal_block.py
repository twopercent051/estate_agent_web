import os
from typing import List

from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from aiogram.fsm.context import FSMContext

from create_bot import bot, config
from tgbot.misc.states import UserFSM
from tgbot.models.sql_connector import TextsDAO
from tgbot.handlers.user.inline import CalculationPriceInline
from tgbot.services.telegraph_service import TelegraphCreatePage

router = Router()

inline = CalculationPriceInline()

admin_group = config.tg_bot.admin_group


@router.callback_query(F.data == "commercial_proposal")
async def commercial_proposal_block(callback: CallbackQuery, state: FSMContext):
    text = await TextsDAO.get_text(chapter="album_photo")
    kb = inline.home_kb()
    await state.set_state(UserFSM.album_photo)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.photo, UserFSM.album_photo)
async def commercial_proposal_block(message: Message, state: FSMContext, album: List[Message] = None):
    media_list = []
    if album is not None:
        for msg in album:
            file_id = msg.photo[-1].file_id
            media_list.append(file_id)
    else:
        file_id = message.photo[-1].file_id
        media_list.append(file_id)
    await state.update_data(album_photo=media_list)
    text = await TextsDAO.get_text(chapter="calc_photo")
    kb = inline.home_kb()
    await state.set_state(UserFSM.calc_photo)
    await message.answer(text, reply_markup=kb)


@router.message(F.photo, UserFSM.calc_photo)
async def commercial_proposal_block(message: Message, state: FSMContext):
    state_data = await state.get_data()
    album_photo = state_data["album_photo"]
    album_files = []
    for i, photo_id in enumerate(album_photo, start=1):
        file_name = f"{message.from_user.id}_album_photo_{i}.jpg"
        await bot.download(file=photo_id, destination=file_name)
        album_files.append(file_name)
    file_name = f"{message.from_user.id}_calc_photo.jpg"
    await bot.download(file=message.photo[-1].file_id, destination=f"{message.from_user.id}_calc_photo.jpg")
    author_name = message.from_user.username if message.from_user.username else "Автор"
    page = TelegraphCreatePage.create_page(album_photos=album_files, calc_photo=file_name, author=author_name)
    for file in album_files:
        os.remove(file)
    os.remove(file_name)
    text = await TextsDAO.get_text(chapter="proposal_result")
    text = f"{text}\n{page}"
    kb = inline.home_kb()
    await message.answer(text, reply_markup=kb, disable_web_page_preview=True)
