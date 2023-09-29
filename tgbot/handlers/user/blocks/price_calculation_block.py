import itertools
import os

from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hcode

from create_bot import bot, config
from tgbot.handlers.admin.main_block import excel_file
from tgbot.misc.states import UserFSM
from tgbot.models.sql_connector import FilesDAO, TextsDAO, UsersDAO
from tgbot.handlers.user.inline import CalculationPriceInline

router = Router()

inline = CalculationPriceInline()

admin_group = config.tg_bot.admin_group


@router.callback_query(F.data == "price_calculation")
async def price_calculation_block(callback: CallbackQuery, state: FSMContext):
    text = await TextsDAO.get_text(chapter="net_to_seller")
    kb = inline.home_kb()
    await state.set_state(UserFSM.net_to_seller)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, UserFSM.net_to_seller)
async def price_calculation_block(message: Message, state: FSMContext):
    try:
        value = int(message.text)
        text = await TextsDAO.get_text(chapter="there_are_payments")
        kb = inline.there_are_payments_kb()
        await state.update_data(net_to_seller=value, payments=[])
    except ValueError:
        text = await TextsDAO.get_text(chapter="not_integer")
        kb = inline.home_kb()
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "payments_yes")
async def price_calculation_block(callback: CallbackQuery, state: FSMContext):
    text = await TextsDAO.get_text(chapter="enter_date")
    kb = inline.home_kb()
    await state.set_state(UserFSM.payment_date)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, UserFSM.payment_date)
async def price_calculation_block(message: Message, state: FSMContext):
    text = await TextsDAO.get_text(chapter="enter_payment")
    kb = inline.home_kb()
    await state.update_data(payment_date=message.text)
    await state.set_state(UserFSM.payment_value)
    await message.answer(text, reply_markup=kb)


@router.message(F.text, UserFSM.payment_value)
async def price_calculation_block(message: Message, state: FSMContext):
    try:
        value = int(message.text)
        text = await TextsDAO.get_text(chapter="continue_payments")
        kb = inline.break_payments_kb()
        state_data = await state.get_data()
        payment_date = state_data["payment_date"]
        payments: list = state_data["payments"]
        payment_data = dict(payment_date=payment_date, payment_value=value)
        payments.append(payment_data)
        await state.update_data(payments=payments)
        await state.set_state(UserFSM.payment_date)
    except ValueError:
        text = await TextsDAO.get_text(chapter="not_integer")
        kb = inline.home_kb()
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "payments_no")
async def price_calculation_block(callback: CallbackQuery, state: FSMContext):
    text = await TextsDAO.get_text(chapter="calculation_result")
    kb = inline.home_kb()
    state_data = await state.get_data()
    file_name = excel_file.calculation_path
    print(state_data["net_to_seller"])
    print(state_data["payments"])
    excel_file.create_calculation_file(net_to_seller=state_data["net_to_seller"], payments=state_data["payments"])
    file = FSInputFile(path=file_name, filename=file_name)
    await state.set_state(UserFSM.home)
    await callback.message.answer_document(document=file, caption=text, reply_markup=kb)
    os.remove(path=excel_file.calculation_path)
    await bot.answer_callback_query(callback.id)
