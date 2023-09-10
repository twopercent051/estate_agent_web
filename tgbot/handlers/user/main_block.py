from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext

from create_bot import bot, config
from tgbot.misc.states import UserFSM
from tgbot.models.sql_connector import FilesDAO
from .inline import InlineKeyboard

router = Router()

inline = InlineKeyboard()

admin_group = config.tg_bot.admin_group


async def start_render(user_id: str | int):
    text = [
        "🏢 Welcome to <b>Brochure Finder!</b> 🌴\n",
        "🔍 Looking for a building brochure in the UAE? You've come to the right place!",
        "I can quickly provide you with a detailed presentation in a convenient PDF format. All you need to do is "
        "enter a keyword or the name of the residential complex you're interested in.\n",
        "📍 Examples <b>of Search Queries:</b>",
        '"Mulberry," "Beach Vista," "Damac Heights"\n',
        "📂 <b>How Does It Work?</b>",
        "1️⃣ Enter your keyword or name",
        "2️⃣ Receive the presentation in PDF format right here",
        "3️⃣ Sell beautifully!\n",
        "📞 <b>Didn't Find the Information You Need?</b>",
        "If you couldn't find the presentation for the project you're interested in, just let us know. We will "
        "definitely add the missing information to our database.\n",
        "👇 <b>Let's get started!</b> Enter your search query now."
    ]
    await bot.send_message(chat_id=user_id, text="\n".join(text))


@router.message(Command("start"))
async def main_block(message: Message, state: FSMContext):
    await start_render(user_id=message.from_user.id)
    await state.set_state(UserFSM.home)


@router.callback_query(F.data == "home")
async def main_block(callback: CallbackQuery, state: FSMContext):
    await start_render(user_id=callback.from_user.id)
    await state.set_state(UserFSM.home)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, UserFSM.home)
async def main_block(message: Message):
    keyword = message.text.lower().replace("_", " ")
    files = await FilesDAO.get_many_by_keyword(keyword=keyword)
    kb = inline.support_kb()
    if len(files) == 0:
        text = "Nothing found 🤷"
        await message.answer(text, reply_markup=kb)
    elif len(files) == 1:
        await message.answer_document(document=files[0]["file_id"], reply_markup=kb)
    else:
        media_group = []
        for file in files[:50]:
            media_group.append(dict(media=file["file_id"], type="document"))
        await message.answer_media_group(media_group)
        text = f"We found {len(files)} options for you"
        await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "support")
async def main_block(callback: CallbackQuery, state: FSMContext):
    text = "Write your question. We will respond soon"
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
    text = "The message has been sent"
    kb = inline.home_kb()
    await state.set_state(UserFSM.home)
    await message.answer(text, reply_markup=kb)
