from typing import List

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F, Router

from create_bot import bot, config
from .filters import AdminFilter
from .inline import InlineKeyboard
from tgbot.misc.states import AdminFSM
from ...models.sql_connector import FilesDAO

router = Router()
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())

admin_group = config.tg_bot.admin_group

inline = InlineKeyboard()


async def start_render():
    text = "Главное меню администратора"
    kb = inline.main_menu_kb()
    await bot.send_message(chat_id=admin_group, text=text, reply_markup=kb)


@router.message(Command("start"))
async def main_block(message: Message, state: FSMContext):
    await start_render()
    await state.set_state(AdminFSM.home)


@router.callback_query(F.data == "home")
async def main_block(callback: CallbackQuery, state: FSMContext):
    await start_render()
    await state.set_state(AdminFSM.home)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data == "upload_files")
async def main_block(callback: CallbackQuery, state: FSMContext):
    text = "Загрузите файлы"
    kb = inline.home_kb()
    await state.set_state(AdminFSM.get_files)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.document)
async def main_block(message: Message, album: List[Message] = None):
    files_list = []
    if album:
        for file in album:
            file_data = dict(file_name=file.document.file_name.replace("_", " ").lower(),
                             file_id=file.document.file_id)
            files_list.append(file_data)
    else:
        file_data = dict(file_name=message.document.file_name.replace("_", " ").lower(),
                         file_id=message.document.file_id)
        files_list =[file_data]
    await FilesDAO.create_many(files=files_list)
    text = f"Добавлено {len(files_list)} файлов"
    kb = inline.home_kb()
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "search_files")
async def main_block(callback: CallbackQuery, state: FSMContext):
    text = "Введите ключевой запрос"
    kb = inline.home_kb()
    await state.set_state(AdminFSM.search_files)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, AdminFSM.search_files)
async def main_block(message: Message):
    keyword = message.text.lower().replace("_", " ")
    files = await FilesDAO.get_many_by_keyword(keyword=keyword)
    if len(files) == 0:
        text = "Ничего не найдено 🤷"
        await message.answer(text)
        return
    for file in files[:50]:
        kb = inline.delete_kb(file_id=file["id"])
        await message.answer_document(document=file["file_id"], reply_markup=kb)
    text = "Чтобы удалить файл из Базы данных нажмите клавишу под ним"
    if len(files) > 50:
        text = f"{text}\nПоказано 50 из {len(files)} файлов"
    kb = inline.home_kb()
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.split(":")[0] == "delete")
async def main_block(callback: CallbackQuery):
    file_id = int(callback.data.split(":")[1])
    await callback.message.edit_reply_markup(reply_markup=None)
    await FilesDAO.delete(id=file_id)
    text = "Файл удалён"
    kb = inline.home_kb()
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "support")
async def main_block(callback: CallbackQuery, state: FSMContext):
    user_id = callback.data.split(":")[1]
    text = "Введите ответ"
    kb = inline.home_kb()
    await state.set_state(AdminFSM.support)
    await state.update_data(user_id=user_id)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, AdminFSM.support)
@router.message(F.photo, AdminFSM.support)
@router.message(F.document, AdminFSM.support)
async def main_block(message: Message, state: FSMContext):
    state_data = await state.get_data()
    user_id = state_data["user_id"]
    text = f"⚠️ Message from support:\n\n{message.text}"
    kb = inline.answer_kb()
    if message.content_type == "text":
        await bot.send_message(chat_id=user_id, text=text, reply_markup=kb)
    if message.content_type == "photo":
        photo_id = message.photo[-1].file_id
        await bot.send_photo(chat_id=user_id, photo=photo_id, caption=text, reply_markup=kb)
    if message.content_type == "document":
        document_id = message.document.file_id
        await bot.send_document(chat_id=user_id, document=document_id, caption=text, reply_markup=kb)
    text = "The message has been sent"
    kb = inline.home_kb()
    await state.set_state(AdminFSM.home)
    await message.answer(text, reply_markup=kb)
