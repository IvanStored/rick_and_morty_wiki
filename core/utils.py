import json

import requests
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from core.loader import (
    CHARACTER_COUNT,
    LOCATION_URL,
    CHARACTER_URL,
    Marker,
    bot,
    filtered_results_file,
)


def make_message_text(entity_info: dict, marker: str) -> str:
    name = f"*Name:* {entity_info['name']}"
    type_ = f"*Type:* {entity_info['type']}"
    message_text = ""
    if marker == "character":
        status = f"*Status:* {entity_info['status']}"
        species = f"*Species:* {entity_info['species']}"
        gender = f"*Gender:* {entity_info['gender']}"
        origin = f"*Origin:* {entity_info['origin']['name']}"
        location = f"*Last known location:* {entity_info['location']['name']}"
        message_text = f"{name}\n{status}\n{species}\n{type_}\n{gender}\n{origin}\n{location}"
    elif marker == "location":
        dimension = f"*Dimension:* {entity_info['dimension']}"
        message_text = f"{name}\n{type_}\n{dimension}"

    return message_text


def make_buttons(
    page: int,
    left: int,
    right: int,
    entity_info: dict,
    _type: str = None,
    pages: int = CHARACTER_COUNT,
    _filter: bool = False,
) -> (
    tuple[
        InlineKeyboardButton,
        InlineKeyboardButton,
        InlineKeyboardButton,
        InlineKeyboardButton,
        InlineKeyboardButton,
    ]
    | tuple[InlineKeyboardButton, InlineKeyboardButton, InlineKeyboardButton]
):
    callback_data_f = f"tof {left} {_type}"
    callback_data_r = f"tof {right} {_type}"
    left_button = InlineKeyboardButton(
        "←", callback_data=f"to {left}" if not _filter else callback_data_f
    )
    page_button = InlineKeyboardButton(
        f"{str(page)}/{str(pages)}", callback_data="_"
    )
    right_button = InlineKeyboardButton(
        "→", callback_data=f"to {right}" if not _filter else callback_data_r
    )
    if not _filter:
        origin_button = InlineKeyboardButton(
            "Info about origin",
            callback_data=entity_info["origin"]["url"]
            if entity_info["origin"]["url"]
            else "unknown",
        )
        location_button = InlineKeyboardButton(
            "Info about location",
            callback_data=entity_info["location"]["url"]
            if entity_info["location"]["url"]
            else "unknown",
        )
        return (
            left_button,
            page_button,
            right_button,
            origin_button,
            location_button,
        )
    else:
        return left_button, page_button, right_button


def make_keyboard(
    page: int,
    entity_info: dict,
    _type: str = None,
    pages: int = CHARACTER_COUNT,
    _filter: bool = False,
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    left = page - 1 if page != 1 else pages
    right = page + 1 if page != pages else 1
    if not _filter:
        (
            left_button,
            page_button,
            right_button,
            origin_button,
            location_button,
        ) = make_buttons(
            page=page,
            left=left,
            right=right,
            entity_info=entity_info,
            pages=pages,
        )

        keyboard.add(left_button, page_button, right_button)
        keyboard.add(origin_button, location_button)
    else:
        (
            left_button,
            page_button,
            right_button,
        ) = make_buttons(
            page=page,
            left=left,
            right=right,
            entity_info=entity_info,
            pages=pages,
            _filter=_filter,
            _type=_type,
        )
        keyboard.add(left_button, page_button, right_button)
    return keyboard


def save_filtered_results(
    json_data: dict, search_params: dict, url: str
) -> None:
    pages_count = json_data["info"]["pages"]
    data_to_write = []

    if pages_count > 1:
        for page_q in range(1, pages_count + 1):
            search_params["page"] = page_q
            data = requests.get(url=url, params=search_params).json()
            data_to_write.extend(data["results"])
    else:
        data_to_write.extend(json_data["results"])

    with open(filtered_results_file, "w") as file:
        json.dump(data_to_write, file, indent=4)


async def show_filter_results(
    message: Message,
    _type: str = None,
    search_name: str = None,
    page: int = 1,
    previous_message: Message = None,
) -> None | Message:
    if _type == Marker.location:
        url = LOCATION_URL
    if _type == Marker.character:
        url = CHARACTER_URL

    if search_name:
        search_params = {"name": search_name}
        response = requests.get(url=url, params=search_params)
        if response.status_code == 404:
            return await message.reply("No results :(")
        else:
            save_filtered_results(
                json_data=response.json(),
                search_params=search_params,
                url=url,
            )

    with open(filtered_results_file, "r") as file:
        data = json.load(file)

    entity = data[page - 1]
    keyboard = make_keyboard(
        page=page,
        entity_info=entity,
        pages=len(data),
        _filter=True,
        _type=_type,
    )
    message_text = make_message_text(entity_info=entity, marker=_type)
    if _type == Marker.character:
        await message.answer_photo(
            photo=entity["image"],
            caption=message_text,
            reply_markup=keyboard,
        )
    else:
        await message.answer(text=message_text, reply_markup=keyboard)
    try:
        await bot.delete_message(
            chat_id=message.chat.id, message_id=previous_message.message_id
        )
    except AttributeError:
        pass
