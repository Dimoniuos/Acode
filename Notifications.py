import asyncio
from aiogram import Bot
import aiogram
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from server import get_expiration_dates
from DataSet import UsersData
Users = UsersData()

async def notification(bot: Bot, api):
    while True:
        users = get_expiration_dates(await api.inbound.get_by_id(1))
        for user in users:
            #print(user[0], user[1], user[2])
            if user[0] == 0 and user[1] == 12:
                builder = InlineKeyboardBuilder()
                builder.row(InlineKeyboardButton(text="Продлить", callback_data="buy"))
                await bot.send_message(user[2], "Ваша подписка истекает меньше чем через день! Советуем скорее продлить", reply_markup=builder.as_markup())
            if user[0] == 0 and user[1] == 1:
                builder = InlineKeyboardBuilder()
                builder.row(InlineKeyboardButton(text="Продлить", callback_data="buy"))
                Users.update_user(user[2], False)
                await bot.send_message(user[2], "Ваша подписка истекла! Рекомендуем скорее продлить",
                                 reply_markup=builder.as_markup())
        await asyncio.sleep(3600)



