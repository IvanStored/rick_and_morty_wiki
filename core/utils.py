from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


from core.loader import CHARACTER_COUNT


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
    page: int, left: int, right: int, entity_info: dict
) -> tuple[
    InlineKeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardButton,
]:
    left_button = InlineKeyboardButton("←", callback_data=f"to {left}")
    page_button = InlineKeyboardButton(
        f"{str(page)}/{str(CHARACTER_COUNT)}", callback_data="_"
    )
    right_button = InlineKeyboardButton("→", callback_data=f"to {right}")
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


def make_keyboard(page: int, entity_info: dict) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    left = page - 1 if page != 1 else CHARACTER_COUNT
    right = page + 1 if page != CHARACTER_COUNT else 1
    (
        left_button,
        page_button,
        right_button,
        origin_button,
        location_button,
    ) = make_buttons(
        page=page, left=left, right=right, entity_info=entity_info
    )
    keyboard.add(left_button, page_button, right_button)
    keyboard.add(origin_button, location_button)
    return keyboard
