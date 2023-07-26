import json
import random

import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import Message, CallbackQuery

from loguru import logger
from requests.exceptions import MissingSchema

from core.loader import (
    dp,
    bot,
    CHARACTER_COUNT,
    Marker,
    LOCATION_COUNT,
    LOCATION_URL,
    CHARACTER_URL,
    EntityForm,
    all_characters_file,
)
from api_requests import gather_data
from core.utils import (
    make_message_text,
    make_keyboard,
    show_filter_results,
)


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: Message) -> None:
    message_text = (
        f"Hello, this is bot for https://rickandmortyapi.com/. You can use next commands:\n"
        f"/all_characters - to get info about all {CHARACTER_COUNT} heroes from Rick and Morty\n"
        f"/random_character - info about random character\n"
        f"/random_location - info about random location\n"
        f"/find_location - filter locations by name\n"
        f"/filter_characters - filter character by name"
    )
    await message.answer(text=message_text, parse_mode=types.ParseMode.HTML)
    await gather_data()


@dp.message_handler(Command("all_characters"))
async def all_characters(
    message: Message, page: int = 1, previous_message: Message = None
) -> None:
    with open(all_characters_file, "r") as file:
        data = json.load(file)

    character_info = data[page - 1]

    text_message = make_message_text(
        entity_info=character_info, marker=Marker.character
    )
    keyboard = make_keyboard(page=page, entity_info=character_info)
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
    if callback.data.startswith("tof"):
        return await show_filter_results(
            message=callback.message,
            page=page,
            previous_message=callback.message,
            _type=callback.data.split(" ")[-1],
        )

    return await all_characters(
        message=callback.message, page=page, previous_message=callback.message
    )


@dp.callback_query_handler(lambda callback: not callback.data.startswith("to"))
async def location_info(callback: CallbackQuery) -> Message:
    try:
        location = requests.get(url=callback.data).json()
    except MissingSchema:
        return await callback.answer(text="Origin/location is unknown")

    text = make_message_text(entity_info=location, marker=Marker.location)
    logger.info(f"Get info about {location['name']}")
    return await callback.message.answer(text=text)


@dp.message_handler(Command("random_character"))
async def random_character(message: Message) -> None:
    character = requests.get(
        url=f"{CHARACTER_URL}/{random.randint(1, CHARACTER_COUNT)}"
    ).json()
    text = make_message_text(entity_info=character, marker=Marker.character)
    await message.answer_photo(photo=character["image"], caption=text)
    logger.info(f"Get info about {character['name']}")


@dp.message_handler(Command("random_location"))
async def random_location(message: Message) -> None:
    location = requests.get(
        url=f"{LOCATION_URL}/{random.randint(1, LOCATION_COUNT)}"
    ).json()
    text = make_message_text(entity_info=location, marker=Marker.location)
    await message.answer(text=text)
    logger.info(f"Get info about {location['name']}")


@dp.message_handler(Command("find_location"))
async def input_location(message: Message, state: FSMContext) -> None:
    await message.reply("Type name/part of the name of location:")
    await state.update_data(type=Marker.location)
    await EntityForm.name.set()


@dp.message_handler(Command("filter_characters"))
async def input_name_character(message: Message, state: FSMContext):
    await message.reply("Type name/part of the name of character:")
    await state.update_data(type=Marker.character)
    await EntityForm.name.set()


@dp.message_handler(
    lambda message: not message.text.startswith("/"), state=EntityForm.name
)
async def filter_results(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    await state.finish()
    await message.answer(
        text=f"Here is results, that contains {data['name']}: "
    )
    await show_filter_results(
        message=message, search_name=data["name"], _type=data["type"]
    )
