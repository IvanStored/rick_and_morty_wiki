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
from aiogram.utils.markdown import bold
from loguru import logger
from requests.exceptions import MissingSchema

from core.loader import dp, bot, storage, CHARACTER_COUNT, Marker
from api_requests import gather_data


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: Message) -> None:
    # TODO : welcome message
    await gather_data()


def make_message_text(character_info: dict, marker: str) -> str:
    name = bold("Name: ") + character_info["name"]
    type_ = bold("Type: ") + character_info["type"]
    message_text = ""
    if marker == "character":
        status = bold("Status: ") + character_info["status"]
        species = bold("Species: ") + character_info["species"]
        gender = bold("Gender: ") + character_info["gender"]
        origin = bold("Origin: ") + character_info["origin"]["name"]
        location = bold("Location: ") + character_info["location"]["name"]
        message_text = f"{name}\n{status}\n{species}\n{type_}\n{gender}\n{origin}\n{location}"
    elif marker == "location":
        dimension = bold("Dimension: ") + character_info["dimension"]
        message_text = f"{name}\n{type_}\n{dimension}"

    return (
        message_text.replace("(", "\(")
        .replace(")", "\)")
        .replace("-", "\-")
        .replace(".", "\.")
    )


@dp.message_handler(Command("all_characters"))
async def all_characters(
    message: Message, page: int = 1, previous_message: Message = None
) -> None:
    character_info = await storage.get(name=page)
    character_info = json.loads(character_info.decode("utf-8"))
    buttons = InlineKeyboardMarkup()
    left = page - 1 if page != 1 else CHARACTER_COUNT
    right = page + 1 if page != CHARACTER_COUNT else 1
    left_button = InlineKeyboardButton("←", callback_data=f"to {left}")
    page_button = InlineKeyboardButton(
        f"{str(page)}/{str(CHARACTER_COUNT)}", callback_data="_"
    )
    right_button = InlineKeyboardButton("→", callback_data=f"to {right}")
    origin_button = InlineKeyboardButton(
        "Info about origin",
        callback_data=character_info["origin"]["url"]
        if character_info["origin"]["url"]
        else "unknown",
    )
    location_button = InlineKeyboardButton(
        "Info about location",
        callback_data=character_info["location"]["url"]
        if character_info["location"]["url"]
        else "unknown",
    )
    buttons.add(left_button, page_button, right_button)
    buttons.add(origin_button)
    buttons.add(location_button)

    text_message = make_message_text(
        character_info=character_info, marker=Marker.character
    )

    await message.answer_photo(
        photo=character_info["image"],
        caption=text_message,
        reply_markup=buttons,
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
