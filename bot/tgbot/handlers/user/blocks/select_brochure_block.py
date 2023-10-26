import itertools

from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hcode

from create_bot import bot, config
from tgbot.misc.states import UserFSM
from tgbot.api_models.redis_connector import RedisConnector as rds
from tgbot.api_models.sql_connector import FilesDAO, UsersDAO
from tgbot.handlers.user.inline import SelectBrochureInline

router = Router()
module = "select_brochure_block"
inline = SelectBrochureInline(module=module)

admin_group = config.tg_bot.admin_group


@router.callback_query(F.data == "select_brochure")
async def select_brochure_block(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    text = rds.get_user_text(user_id=user_id, module=module, handler="greeting_select_brochure")
    kb = inline.home_kb(user_id=user_id)
    await state.set_state(UserFSM.search_brochure)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, UserFSM.search_brochure)
async def select_brochure_block(message: Message):
    handler = "found_materials"
    user_id = message.from_user.id
    keyword = message.text.lower().replace("_", " ")
    files = await FilesDAO.get_many_by_keyword(keyword=keyword)
    await UsersDAO.update_requests(user_id=str(message.from_user.id))
    kb = inline.support_kb(user_id=user_id, handler=handler)
    if len(files) == 0:
        # text = await TextsDAO.get_text(chapter="nothing_found")
        text = rds.get_user_text(user_id=user_id, module=module, handler="nothing_found")
        await message.answer(text, reply_markup=kb)
        username = f"@{message.from_user.username}" if message.from_user.username else "---"
        admin_text = f"⚠️ Пользователь {username} по запросу '{hcode(keyword)}' не смог найти материал"
        await bot.send_message(chat_id=admin_group, text=admin_text)
    elif len(files) == 1:
        await message.answer_document(document=files[0]["file_id"], reply_markup=kb)
    else:
        it = iter(files[:50])
        chunks = iter(lambda: tuple(itertools.islice(it, 10)), ())
        for chunk in chunks:
            media_group = []
            for file in chunk:
                media_group.append(dict(media=file["file_id"], type="document"))
            if len(media_group) == 1:
                await message.answer_document(document=media_group[0]["media"])
            else:
                await message.answer_media_group(media_group)
        # text = await TextsDAO.get_text(chapter="found_materials")
        text = rds.get_user_text(user_id=user_id, module=module, handler=handler)
        await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "support")
async def select_brochure_block(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    # text = await TextsDAO.get_text(chapter="write_request")
    text = rds.get_user_text(user_id=user_id, module=module, handler="write_request")
    kb = inline.home_kb(user_id=user_id)
    await state.set_state(UserFSM.support)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, UserFSM.support)
@router.message(F.photo, UserFSM.support)
@router.message(F.document, UserFSM.support)
async def select_brochure_block(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else "---"
    kb = inline.answer_user_kb(user_id=message.from_user.id)
    text = f"⚠️ Сообщение от пользователя {username}:\n\n{message.text}"
    if message.content_type == "text":
        await bot.send_message(chat_id=admin_group, text=text, reply_markup=kb)
    if message.content_type == "photo":
        photo_id = message.photo[-1].file_id
        await bot.send_photo(chat_id=admin_group, photo=photo_id, caption=text, reply_markup=kb)
    if message.content_type == "document":
        document_id = message.document.file_id
        await bot.send_document(chat_id=admin_group, document=document_id, caption=text, reply_markup=kb)
    text = rds.get_user_text(user_id=user_id, module=module, handler="message_sent")
    kb = inline.home_kb(user_id=user_id)
    await state.set_state(UserFSM.home)
    await message.answer(text, reply_markup=kb)
