from yookassa import Payment, Configuration, payment
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import uuid
import asyncio
from aiogram import Bot
import os
from dotenv import load_dotenv
load_dotenv()
Configuration.account_id = os.getenv("pay_account_id")
Configuration.secret_key = os.getenv("pay_shop_id")
from server import list_active_users, get_expiration_dates_sl, get_connection_string
from py3xui import AsyncApi
import server
from DataSet import UsersData, Refferals
users = UsersData()
refferal = Refferals()


def create(email : str, value : str):
    idempotence_key = str(uuid.uuid4())
    payment = Payment.create({
    "amount": {
      "value": value,
      "currency": "RUB"
    },
    "confirmation": {
      "type": "redirect",
        "return_url": "https://t.me/Acodebot",
    },
    "capture": True,
    "description": "Подписка AcodeVpn на 30 дней",
    "receipt": {
        "customer": {
            "email": email,
        },
        "items": [
            {
                "description": "Подписка AcodeVpn на 30 дней",
                "quantity": 1,
                "amount": {
                    "value": value,
                    "currency": "RUB"
                },
                "vat_code": 1,
            }
        ]
    }

    }, idempotence_key)
    confirmation_url = payment.confirmation.confirmation_url
    return confirmation_url, payment.id



async def check_payment(id, payment_id, bot : Bot, api : AsyncApi):
    if not payment_id:
        return
    for i in range(90):
        status = Payment.find_one(payment_id=payment_id)["status"]
        if status == "succeeded":
            if id not in list_active_users(await api.inbound.get_by_id(1)):
                await server.prolong_subscriptions(str(id), api, 30, await api.inbound.get_by_id(1))
                key = get_connection_string(await api.inbound.get_by_id(1), str(id))
                await bot.send_message(chat_id=id, text=f'Оплата прошла успешно! \n\nВаш код активации:\n\n<code>{key}</code>',
                                     parse_mode="html")
                users.update_user(id, True)
                refferal.update_sale(id)
                refferal.null_sale(id)
            else:
                await server.prolong_subscriptions(str(id), api, 30, await api.inbound.get_by_id(1))
                key = get_connection_string(await api.inbound.get_by_id(1), str(id))
                await bot.send_message(chat_id=id, text=f'Оплата прошла успешно! \n\nВаш код активации:\n\n<code>{key}</code>',
                                     parse_mode="html")
                users.update_user(id, True)
                refferal.null_sale(id)
            return
        if status == "cancelled":
            await bot.send_message(chat_id=id, text="Оплата была отменена")
            return
        await asyncio.sleep(10)
    await bot.send_message(chat_id=id, text="Время оплаты закончилось")


