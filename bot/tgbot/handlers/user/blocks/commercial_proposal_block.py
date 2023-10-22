import os
from typing import List

from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from aiogram.fsm.context import FSMContext

from bot.create_bot import bot, config
from bot.tgbot.misc.states import UserFSM
from bot.tgbot.models.redis_connector import RedisConnector
from bot.tgbot.models.sql_connector import UsersDAO
from bot.tgbot.handlers.user.inline import CommercialProposalInline
from bot.tgbot.services.telegraph_service import TelegraphCreatePage

router = Router()
module = "commercial_proposal_block"
inline = CommercialProposalInline(module=module)
rds = RedisConnector()

admin_group = config.tg_bot.admin_group


@router.callback_query(F.data == "commercial_proposal")
async def commercial_proposal_block(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    # text = await TextsDAO.get_text(chapter="proposal_title")
    text = rds.get_user_text(user_id=user_id, module=module, handler="net_to_seller")
    kb = inline.home_kb(user_id=user_id)
    await state.set_state(UserFSM.proposal_title)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, UserFSM.proposal_title)
async def commercial_proposal_block(message: Message, state: FSMContext):
    user_id = message.from_user.id
    # text = await TextsDAO.get_text(chapter="album_photo")
    text = rds.get_user_text(user_id=user_id, module=module, handler="album_photo")
    kb = inline.home_kb(user_id=user_id)
    await state.set_state(UserFSM.album_photo)
    await state.update_data(album_photo=[], title=message.text)
    await message.answer(text, reply_markup=kb)


@router.message(F.photo, UserFSM.album_photo)
async def commercial_proposal_block(message: Message, state: FSMContext):
    user_id = message.from_user.id
    handler = "album_photo"
    state_data = await state.get_data()
    album_photo: List[str] = state_data["album_photo"]
    album_photo.append(message.photo[-1].file_id)
    await state.update_data(album_photo=album_photo)
    # text = await TextsDAO.get_text(chapter="is_more_photo")
    text = rds.get_user_text(user_id=user_id, module=module, handler=handler)
    kb = inline.upload_layout_photo_kb(user_id=user_id, handler=handler)
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "upload_layout")
async def commercial_proposal_block(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    # text = await TextsDAO.get_text(chapter="layout_photo")
    text = rds.get_user_text(user_id=user_id, module=module, handler="layout_photo")
    kb = inline.home_kb(user_id=user_id)
    await state.set_state(UserFSM.layout_photo)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.photo, UserFSM.layout_photo)
async def commercial_proposal_block(message: Message, state: FSMContext):
    user_id = message.from_user.id
    # text = await TextsDAO.get_text(chapter="calc_photo")
    text = rds.get_user_text(user_id=user_id, module=module, handler="calc_photo")
    kb = inline.home_kb(user_id=user_id)
    await state.update_data(layout_photo=message.photo[-1].file_id)
    await state.set_state(UserFSM.calc_photo)
    await message.answer(text, reply_markup=kb)


@router.message(F.text, UserFSM.description)
async def commercial_proposal_block(message: Message, state: FSMContext):
    user_id = message.from_user.id
    # text = await TextsDAO.get_text(chapter="calc_photo")
    text = rds.get_user_text(user_id=user_id, module=module, handler="calc_photo")
    kb = inline.home_kb(user_id=user_id)
    await state.update_data(description=message.text)
    await state.set_state(UserFSM.calc_photo)
    await message.answer(text, reply_markup=kb)


@router.message(F.photo, UserFSM.calc_photo)
async def commercial_proposal_block(message: Message, state: FSMContext):
    user_id = message.from_user.id
    state_data = await state.get_data()
    album_photo = state_data["album_photo"]
    layout_photo = state_data["layout_photo"]
    album_files = []
    for i, photo_id in enumerate(album_photo, start=1):
        file_name = f"{message.from_user.id}_album_photo_{i}.jpg"
        await bot.download(file=photo_id, destination=file_name)
        album_files.append(file_name)
    layout_name = f"{message.from_user.id}_layout_photo.jpg"
    await bot.download(file=layout_photo, destination=layout_name)
    calc_name = f"{message.from_user.id}_calc_photo.jpg"
    await bot.download(file=message.photo[-1].file_id, destination=calc_name)
    page = await TelegraphCreatePage.create_page(user_id=user_id,
                                                 title=state_data["title"],
                                                 album_photos=album_files,
                                                 layout_photo=layout_name,
                                                 calc_photo=calc_name,
                                                 author=message.from_user.username)
    for file in album_files:
        os.remove(file)
    os.remove(layout_name)
    os.remove(calc_name)
    # text = await TextsDAO.get_text(chapter="proposal_result")
    text = rds.get_user_text(user_id=user_id, module=module, handler="proposal_result")
    text = f"{text}\n{page}"
    kb = inline.home_kb(user_id=user_id)
    await message.answer(text, reply_markup=kb, disable_web_page_preview=True)
    username = f"@{message.from_user.username}" if message.from_user.username else "---"
    admin_text = f"Пользователь {username} [{message.from_user.id}] сгенерировал отчёт {page}"
    await UsersDAO.update_telegraph_count(user_id=str(message.from_user.id))
    await bot.send_message(chat_id=admin_group, text=admin_text, disable_web_page_preview=True)
