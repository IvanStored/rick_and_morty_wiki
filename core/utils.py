from aiogram.utils.markdown import bold


def make_message_text(character_info: dict, marker: str) -> str:
    name = bold("Name: ") + character_info["name"]
    type_ = bold("Type: ") + character_info["type"]
    message_text = ""
    if marker == "character":
        status = bold("Status: ") + character_info["status"]
        species = bold("Species: ") + character_info["species"]
        gender = bold("Gender: ") + character_info["gender"]
        origin = bold("Origin: ") + character_info["origin"]["name"]
        location = (
            bold("Last known location: ") + character_info["location"]["name"]
        )
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
