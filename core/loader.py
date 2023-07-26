import os

import requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from dotenv import load_dotenv


load_dotenv()
CHARACTER_URL = os.getenv("CHARACTER_URL")
LOCATION_URL = os.getenv("LOCATION_URL")
CHARACTER_PAGES_COUNT = requests.get(url=CHARACTER_URL).json()["info"]["pages"]
CHARACTER_COUNT = requests.get(url=CHARACTER_URL).json()["info"]["count"]
LOCATION_COUNT = requests.get(url=LOCATION_URL).json()["info"]["count"]
token = os.getenv("BOT_TOKEN")
bot = Bot(token=token, parse_mode=types.ParseMode.MARKDOWN)
dp = Dispatcher(bot, storage=MemoryStorage())
filtered_results_file = "locations.json"
all_characters_file = "all_characters.json"


class Marker:
    character = "character"
    location = "location"


class EntityForm(StatesGroup):
    name = State()
    type = State()
