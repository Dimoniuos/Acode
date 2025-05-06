from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
import logging
import asyncio
from aiogram.filters import Command, StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from re import match
from dotenv import load_dotenv
import os
import Notifications
from payment import create, check_payment
import server
from Partners import Partners
from server import list_active_users, get_expiration_dates_sl, get_connection_string

load_dotenv()
from py3xui import AsyncApi
api = AsyncApi(host=os.getenv("panel_host"), username=os.getenv("panel_login"), password=os.getenv("panel_password"))
from DataSet import UsersData, Refferals, Price, AllRefferals

logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.getenv("bot_token"))
dp = Dispatcher()
refferal = Refferals()
users = UsersData()
price = Price()
partners = Partners()
AllRefferals = AllRefferals()
admin_id = os.getenv("admin_id")
router = Router()
dp.include_router(router)

class Emails(StatesGroup):
    Email = State()


@dp.message(Command("start"))
async def start(message: Message):
    if not refferal.Exist(message.from_user.id):
        username = "@"
        if message.from_user.username:
            username += message.from_user.username
        users.insert_user(message.from_user.id, None, username, False)
        if " " in message.text:
            mes, ref = message.text.split()
            refferal.insert_user(message.from_user.id, username, ref, 0)
            AllRefferals.insert_user(message.from_user.id, ref)
            if "P" in message.text:
                partners.update_started(message.text.replace("/start ", ""))
        else:
            refferal.insert_user(message.from_user.id, username, 0, 0)
            AllRefferals.insert_user(message.from_user.id, "")

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Инструкция по активации", url="https://telegra.ph/Instrukciya-po-podklyucheniyu-VPN-04-30-4"))
    if str(message.from_user.id) not in list_active_users(await api.inbound.get_by_id(1)):
        builder.row(InlineKeyboardButton(text="Купить Подписку", callback_data="my_sub"))
    else:
        builder.row(InlineKeyboardButton(text="Моя Подписка", callback_data="my_sub"))
    builder.row(InlineKeyboardButton(text="Реферальная Система", callback_data="refferalsistem"))
    builder.row(InlineKeyboardButton(text="Помощь", callback_data="help"))
    await message.answer("Приветсвуем! Что Вас интересует?", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "help")
async def help(call: CallbackQuery):
    await bot.answer_callback_query(call.id)
    await call.message.edit_text(
        "Задайте Ваш вопрос @AcodeHelper"
    )

@dp.callback_query(F.data=="my_sub")
async def my_sub(call: CallbackQuery):
    await bot.answer_callback_query(call.id)
    await call.message.delete()
    id = str(call.from_user.id)
    if id in list_active_users(await api.inbound.get_by_id(1)):
        times = get_expiration_dates_sl(await api.inbound.get_by_id(1))[id]
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Мой VPN-ключ", callback_data="my_key"))
        if times[0] < 60:
            builder.row(InlineKeyboardButton(text="Продлить подписку", callback_data="buy"))
        await call.message.answer(f"Ваша подписка активна\n До окончания действия подписки: {times[0]} дня(-ей) {times[1]} часа(-ов)", reply_markup=builder.as_markup())
    else:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Приобрести подписку", callback_data="buy"))
        await call.message.answer(f"Ваша подписка не активна", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "refferalsistem")
async def refferalls(call: CallbackQuery):
    await bot.answer_callback_query(call.id)
    await call.message.delete()
    id = str(call.from_user.id)
    if partners.Exist(id)[0]:
        data = partners.get_statistics(id)
        ans = ""
        if data:
            for i in data:
                ans += f"Ссылка: t.me/@acodevpnbot?start={i[0]}\nНажало Start: {i[2]}\nСовершило покупку: {i[3]}\n\n"
        else:
            ans = "У Вас нет активных ссылок"
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Создать ссылку", callback_data="New_link"))
        await call.message.answer(ans, reply_markup=builder.as_markup())
    else:
        await call.message.answer(f"Приглашайте друзей и получайте скидку! \nЗа каждого друга, который оплатит подписку, Вы получаете скидку 20% на оплату или продление подписки\n"
                              f"Максимальная скидка - 100%"
                              f"\n\nВаша текущая скидка: {refferal.get_sale(call.from_user.id)}%\n\n"
                              f"Ваша рефферальная ссылка: t.me/@acodevpnbot?start={id}\n\n"
                              f"Если Вы можете пригласить больше 10 друзей, обращайтесь к @AcodeHelper для получения условий сотрудничества")



@dp.callback_query(F.data == "New_link")
async def new_link(call: CallbackQuery):
    id = str(call.from_user.id)
    await bot.answer_callback_query(call.id)
    link = f"{id}P{len(partners.get_statistics(id)) + 1}"
    partners.insert(link, id)
    await call.message.answer("Новая ссылка:\nt.me/@acodebot?start="+link)



@dp.callback_query(F.data=="my_key")
async def my_key(call: CallbackQuery):
    id = str(call.from_user.id)
    await bot.answer_callback_query(call.id)
    #await call.message.delete()
    if id in list_active_users(await api.inbound.get_by_id(1)):
        key = get_connection_string(await api.inbound.get_by_id(1), id)
        await call.message.edit_text(f'Ваш код активации:\n\n<code>{key}</code>', parse_mode="html")
    else:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Приобрести подписку", callback_data="buy"))
        await call.message.edit_text(f"Ваша подписка не активна", reply_markup=builder.as_markup())


@dp.callback_query(F.data=="buy")
async def my_sub(call: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(call.id)
    await call.message.delete()
    sale = refferal.get_sale(call.from_user.id)
    if sale == 100:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Приобрести", callback_data="buy_for_zero"))
        await call.message.answer('Активация Acode Premium на 30 дней за 0₽\n\nЛокация: Германия 🇩🇪\n\nСовершая покупку, Вы соглашаетесь с <a href="https://telegra.ph/POLZOVATELSKOE-SOGLASHENIE-05-01-9">Условиями пользования</a>', reply_markup=builder.as_markup(), parse_mode="html", disable_web_page_preview=True)
    else:
        email = users.get_email(call.from_user.id)
        if email == None:
            await call.message.answer("Введите пожалуйста Вашу почту для отправки чека. Это нужно сделать только 1 раз")
            await state.set_state(Emails.Email)
        else:
            await start_payment(call.message, call.from_user.id)

@router.message(Emails.Email)
async def _email(message: Message, state: FSMContext):
    mail = message.text
    EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not match(EMAIL_REGEX, mail):
        await message.answer("Неверный формат почты. Попробуйте ещё раз:")
        return
    await state.set_state(None)
    users.update_email(message.from_user.id, mail)
    await start_payment(message, message.from_user.id)



async def start_payment(message: Message, id):
    sale = refferal.get_sale(id)
    email = users.get_email(id)
    builder = InlineKeyboardBuilder()
    cost = price.get_price()
    pay = create(email, cost - cost * sale / 100)
    builder.row(InlineKeyboardButton(text=f"Oплатить {cost - cost * sale / 100 :.2f}₽", url=pay[0]))
    await message.answer('Подписка Acode VPN на 30 дней\n\nЛокация: Германия 🇩🇪\n\nСовершая покупку, Вы соглашаетесь с <a href="https://telegra.ph/POLZOVATELSKOE-SOGLASHENIE-05-01-9">Условиями пользования</a>', reply_markup=builder.as_markup(), parse_mode="html", disable_web_page_preview=True)
    await asyncio.create_task(check_payment(id, pay[1], bot, api))


@dp.callback_query(F.data == "buy_for_zero")
async def succe(call: CallbackQuery):
    await bot.answer_callback_query(call.id)
    id = str(call.from_user.id)
    if id not in list_active_users(await api.inbound.get_by_id(1)):
        await server.prolong_subscriptions(id, api, 30, await api.inbound.get_by_id(1))
        key = get_connection_string(await api.inbound.get_by_id(1), id)
        await call.message.answer(f'Оплата прошла успешно! \n\nВаш код активации:\n\n<code>{key}</code>', parse_mode="html")
        users.update_user(id, True)
        refferal.update_sale(id)
        refferal.null_sale(id)
    else:
        await server.prolong_subscriptions(id, api, 30, await api.inbound.get_by_id(1))
        key = get_connection_string(await api.inbound.get_by_id(1), id)
        await call.message.answer(f'Оплата прошла успешно! \n\nВаш код активации:\n\n<code>{key}</code>', parse_mode="html")
        users.update_user(id, True)
        refferal.null_sale(id)


@router.message(F.photo | F.text,  StateFilter(None))
async def admin_post_all(message: Message):
    if message.from_user.id != int(admin_id):
        return
    if not (message.text or message.caption):
        return
    raw_text = message.caption if message.caption else message.text
    if "/Admin" == raw_text.strip():
        pass
    if "/admin_post_all" in raw_text:
        text = raw_text.replace("/admin_post_all", "").strip()
        image = message.photo[-1].file_id if message.photo else None
        userlist = users.UsersList()
        for user_id in userlist:
            if image:
                await bot.send_photo(chat_id=user_id, photo=image, caption=text)
            else:
                await bot.send_message(chat_id=user_id, text=text)
    elif "/admin_post_person" in raw_text:
        text = raw_text.replace("/admin_post_person", "").strip()
        back = text.find(" ")
        user = int(text[0:back])
        text = text[back:]
        image = message.photo[-1].file_id if message.photo else None
        if image:
            await bot.send_photo(chat_id=user, photo=image, caption=text)
        else:
            await bot.send_message(chat_id=user, text=text)
    elif "/referral_file" in raw_text:
        refferal.get_table()
        await message.answer_document(types.FSInputFile("Refferals.csv"))
    elif "/users_file" in raw_text:
        users.get_table()
        await message.answer_document(types.FSInputFile("Users.csv"))
    elif "/set_price" in raw_text:
        new_price = int(raw_text.replace("/set_price", "").strip())
        price.update_price(new_price)
    elif "/new_partner" in raw_text:
        new_partner = int(raw_text.replace("/new_partner", "").strip())
        users.update_partner(new_partner, True)




async def main():
    await api.login()
    task = asyncio.create_task(Notifications.notification(bot, api))
    await dp.start_polling(bot)
    await task




if __name__ == '__main__':
    asyncio.run(main())





