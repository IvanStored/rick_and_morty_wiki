from aiogram.types import Message

from core.loader import dp


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")


@dp.message_handler()
async def echo(message: Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)

    await message.answer(message.text)
