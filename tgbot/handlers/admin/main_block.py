import asyncio
from typing import List

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram import F, Router

from create_bot import bot, config
from .filters import AdminFilter
from .inline import InlineKeyboard
from tgbot.misc.states import AdminFSM
from ...models.sql_connector import FilesDAO, TextsDAO, UsersDAO
from ...services.excel import ExcelFile

router = Router()
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())

admin_group = config.tg_bot.admin_group

inline = InlineKeyboard()

excel_file = ExcelFile()


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
        files_list = [file_data]
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
    text = await TextsDAO.get_text(chapter="message_from_support")
    text = f"{text}\n\n{message.text}"
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


@router.callback_query(F.data == "edit_texts")
async def main_block(callback: CallbackQuery):
    text = "Выберите что редактируем"
    kb = inline.edit_texts_kb()
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "edit_text")
async def main_block(callback: CallbackQuery, state: FSMContext):
    chapter = callback.data.split(":")[1]
    text = await TextsDAO.get_text(chapter=chapter)
    await callback.message.answer(text)
    is_text = True
    if text == "ТЕКСТ НЕ ЗАДАН":
        is_text = False
    await asyncio.sleep(1)
    text = "Сейчас текст такой 👆. Введите новый или вернитесь в главное меню"
    kb = inline.home_kb()
    await state.set_state(AdminFSM.edit_text)
    await state.update_data(chapter=chapter, is_text=is_text)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, AdminFSM.edit_text)
async def main_block(message: Message, state: FSMContext):
    state_data = await state.get_data()
    chapter = state_data["chapter"]
    is_text = state_data["is_text"]
    if is_text:
        await TextsDAO.update_by_chapter(chapter=chapter, text=message.html_text)
    else:
        await TextsDAO.create(chapter=chapter, text=message.html_text)
    text = "👍 Обновили"
    kb = inline.main_menu_kb()
    await state.set_state(AdminFSM.home)
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "statistics")
async def main_block(callback: CallbackQuery):
    users = await UsersDAO.get_order_by_count()
    text = f"Сейчас зарегистрировано {len(users)} пользователей"
    kb = inline.home_kb()
    excel_file.create_users_file(users=users)
    file_name = excel_file.users_path
    file = FSInputFile(path=file_name, filename=file_name)
    await callback.message.answer_document(document=file, caption=text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data == "mailing")
async def main_block(callback: CallbackQuery, state: FSMContext):
    text = "Введите текст сообщения. Можно приложить 1 фото или 1 видео"
    kb = inline.home_kb()
    await state.set_state(AdminFSM.mailing)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, AdminFSM.mailing)
@router.message(F.photo, AdminFSM.mailing)
@router.message(F.video, AdminFSM.mailing)
async def main_block(message: Message, state: FSMContext):
    users = await UsersDAO.get_many()
    count = 0
    for user in users:
        user_id = user["user_id"]
        try:
            if message.content_type == "text":
                await bot.send_message(chat_id=user_id, text=message.html_text)
            if message.content_type == "photo":
                await bot.send_photo(chat_id=user_id, photo=message.photo[-1].file_id, caption=message.caption)
            if message.content_type == "video":
                await bot.send_video(chat_id=user_id, video=message.video.file_id, caption=message.caption)
            count += 1
        except:
            pass
    text = f"Сообщение доставлено {count} / {len(users)} пользователей"
    kb = inline.home_kb()
    await state.set_state(AdminFSM.home)
    await message.answer(text, reply_markup=kb)
