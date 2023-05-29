import os

import requests
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv
from redis.asyncio.client import Redis


load_dotenv()
CHARACTER_URL = os.getenv("CHARACTER_URL")
LOCATION_URL = os.getenv("LOCATION_URL")
CHARACTER_PAGES_COUNT = requests.get(url=CHARACTER_URL).json()["info"]["pages"]
CHARACTER_COUNT = requests.get(url=CHARACTER_URL).json()["info"]["count"]
LOCATION_COUNT = requests.get(url=LOCATION_URL).json()["info"]["count"]
token = os.getenv("BOT_TOKEN")
bot = Bot(token=token, parse_mode=types.ParseMode.MARKDOWN)
dp = Dispatcher(bot)
storage = Redis(
    host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT"))
)


class Marker:
    character = "character"
    location = "location"
