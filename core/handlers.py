import json
import random

import requests
from aiogram.dispatcher.filters import Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from loguru import logger
from requests.exceptions import MissingSchema

from core.loader import dp, bot, storage, CHARACTER_COUNT, Marker
from api_requests import gather_data
from core.utils import make_message_text, make_keyboard


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: Message) -> None:
    # TODO : welcome message
    await gather_data()


@dp.message_handler(Command("all_characters"))
async def all_characters(
    message: Message, page: int = 1, previous_message: Message = None
) -> None:
    character_info = await storage.get(name=page)
    character_info = json.loads(character_info.decode("utf-8"))

    text_message = make_message_text(
        character_info=character_info, marker=Marker.character
    )
    keyboard = make_keyboard(page=page, character_info=character_info)
    await message.answer_photo(
        photo=character_info["image"],
        caption=text_message,
        reply_markup=keyboard,
    )
    logger.info(f"Get info about {character_info['name']}")
    try:
        await bot.delete_message(
            chat_id=message.chat.id, message_id=previous_message.message_id
        )
    except AttributeError:
        pass


@dp.callback_query_handler(lambda callback: callback.data.startswith("to"))
async def pagination(callback: CallbackQuery) -> None:
    page = int(callback.data.split(" ")[1])

    return await all_characters(
        message=callback.message, page=page, previous_message=callback.message
    )


@dp.callback_query_handler(lambda callback: not callback.data.startswith("to"))
async def location_info(callback: CallbackQuery) -> Message:
    try:
        location = requests.get(url=callback.data).json()
    except MissingSchema:
        return await callback.answer(text="Origin/location is unknown")

    text = make_message_text(character_info=location, marker=Marker.location)
    logger.info(f"Get info about {location['name']}")
    return await callback.message.answer(text=text)


@dp.message_handler(Command("random_character"))
async def random_character(message: Message) -> None:
    character = await storage.get(name=random.randint(1, CHARACTER_COUNT))
    character = json.loads(character.decode("utf-8"))
    text = make_message_text(character_info=character, marker=Marker.character)
    await message.answer_photo(photo=character["image"], caption=text)
    logger.info(f"Get info about {character['name']}")
