import os

from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram import F, Router
from aiogram.fsm.context import FSMContext

from create_bot import bot, config
from tgbot.handlers.admin.main_block import excel_file
from tgbot.misc.states import UserFSM
from tgbot.api_models.redis_connector import RedisConnector as rds
from tgbot.api_models.sql_connector import UsersDAO
from tgbot.handlers.user.inline import CalculationPriceInline

router = Router()
module = "price_calculation_block"
inline = CalculationPriceInline(module=module)

admin_group = config.tg_bot.admin_group


@router.callback_query(F.data == "price_calculation")
async def price_calculation_block(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    # text = await TextsDAO.get_text(chapter="net_to_seller")
    text = rds.get_user_text(user_id=user_id, module=module, handler="net_to_seller")
    kb = inline.home_kb(user_id=user_id)
    await state.set_state(UserFSM.net_to_seller)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, UserFSM.net_to_seller)
async def price_calculation_block(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        value = int(message.text)
        handler = "there_are_payments"
        # text = await TextsDAO.get_text(chapter="there_are_payments")
        text = rds.get_user_text(user_id=user_id, module=module, handler=handler)
        kb = inline.there_are_payments_kb(user_id=user_id, handler=handler)
        await state.update_data(net_to_seller=value, payments=[])
    except ValueError:
        # text = await TextsDAO.get_text(chapter="not_integer")
        text = rds.get_user_text(user_id=user_id, module=module, handler="not_integer")
        kb = inline.home_kb(user_id=user_id)
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "payments_yes")
async def price_calculation_block(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    text = rds.get_user_text(user_id=user_id, module=module, handler="enter_date")
    kb = inline.home_kb(user_id=user_id)
    await state.set_state(UserFSM.payment_date)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, UserFSM.payment_date)
async def price_calculation_block(message: Message, state: FSMContext):
    user_id = message.from_user.id
    # text = await TextsDAO.get_text(chapter="enter_payment")
    text = rds.get_user_text(user_id=user_id, module=module, handler="enter_payment")
    kb = inline.home_kb(user_id=user_id)
    await state.update_data(payment_date=message.text)
    await state.set_state(UserFSM.payment_value)
    await message.answer(text, reply_markup=kb)


@router.message(F.text, UserFSM.payment_value)
async def price_calculation_block(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        value = int(message.text)
        handler = "continue_payments"
        # text = await TextsDAO.get_text(chapter="continue_payments")
        text = rds.get_user_text(user_id=user_id, module=module, handler=handler)
        kb = inline.break_payments_kb(user_id=user_id, handler=handler)
        state_data = await state.get_data()
        payment_date = state_data["payment_date"]
        payments: list = state_data["payments"]
        payment_data = dict(payment_date=payment_date, payment_value=value)
        payments.append(payment_data)
        await state.update_data(payments=payments)
        await state.set_state(UserFSM.payment_date)
    except ValueError:
        # text = await TextsDAO.get_text(chapter="not_integer")
        text = rds.get_user_text(user_id=user_id, module=module, handler="not_integer")
        kb = inline.home_kb(user_id=user_id)
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "payments_no")
async def price_calculation_block(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    # text = await TextsDAO.get_text(chapter="calculation_result")
    text = rds.get_user_text(user_id=user_id, module=module, handler="calculation_result")
    kb = inline.home_kb(user_id=user_id)
    state_data = await state.get_data()
    file_name = excel_file.calculation_path
    excel_file.create_calculation_file(net_to_seller=state_data["net_to_seller"], payments=state_data["payments"])
    file = FSInputFile(path=file_name, filename=file_name)
    await state.set_state(UserFSM.home)
    await callback.message.answer_document(document=file, caption=text, reply_markup=kb)
    username = f"@{callback.from_user.username}" if callback.from_user.username else "---"
    admin_text = f"Пользователь {username} [{callback.from_user.id}] сгенерировал расчёт"
    await UsersDAO.update_calculation(user_id=str(callback.from_user.id))
    await bot.send_document(chat_id=admin_group, document=file, caption=admin_text)
    os.remove(path=excel_file.calculation_path)
    await bot.answer_callback_query(callback.id)
