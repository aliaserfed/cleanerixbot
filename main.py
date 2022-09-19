import logging
import os

from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

api_id = 18309539
api_hash = '7ae08383a0b2feffe4223c9f44164fa3'

client = TelegramClient('session', api_id, api_hash)
client.start()

TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)


async def dump_all_messages(channel):
    """Записывает json-файл с информацией о всех сообщениях канала/чата"""
    offset_msg = 0  # номер записи, с которой начинается считывание
    limit_msg = 100  # максимальное число записей, передаваемых за один раз

    all_messages = []  # список всех сообщений
    total_count_limit = 0  # поменяйте это значение, если вам нужны не все сообщения

    while True:
        history = await client(GetHistoryRequest(
            peer=channel,
            offset_id=offset_msg,
            offset_date=None, add_offset=0,
            limit=limit_msg, max_id=0, min_id=0,
            hash=0))
        if not history.messages:
            break
        messages = history.messages
        for message in messages:
            all_messages.append(message.to_dict())
        offset_msg = messages[len(messages) - 1].id
        total_messages = len(all_messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break

    messages_id = list()
    for i, message in enumerate(all_messages):
        if message['_'] == 'MessageService' and message['action']['_'] != 'MessageActionChannelMigrateFrom':
            messages_id.append(message['id'])
    return messages_id


@dp.message_handler(commands=['clear'])
async def delete_message_service(message: Message):
    print(message.chat.id)
    try:
        if message.from_user.id == 1616210594 and message.chat.id != message.from_user.id:
            await message.delete()
            channel = await client.get_entity(-1001693301776)
            # channel = await client.get_entity(-1001241670968)
            # await dump_all_messages(channel)
            for message_id in await dump_all_messages(channel):
                await bot.delete_message(-1001693301776, message_id)
    except:
        pass


@dp.message_handler(content_types=['new_chat_members', 'left_chat_member'])
async def delete_new_message_service(message: Message):
    try:
        await message.delete()
    except:
        pass


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
