from core.loader import storage, CHARACTER_PAGES_COUNT, CHARACTER_URL

import asyncio
import json

import aiohttp
from aiohttp import ClientSession


def without_specified_keys(character_info: dict) -> dict:
    invalid_keys = {"created", "url"}
    return {
        key: value
        for key, value in character_info.items()
        if key not in invalid_keys
    }


async def get_character_data(session: ClientSession, page: int) -> None:
    async with session.get(
        url=CHARACTER_URL,
        params={"page": page},
    ) as response:
        response_json = await response.json()
        characters = response_json["results"]

        for character in characters:
            character_info = without_specified_keys(character_info=character)
            await storage.set(
                name=character["id"],
                value=json.dumps(character_info).encode("utf-8"),
            )


async def gather_data() -> None:
    async with aiohttp.ClientSession() as session:
        tasks = []

        for page in range(1, CHARACTER_PAGES_COUNT + 1):
            task = asyncio.create_task(get_character_data(session, page))
            tasks.append(task)

        await asyncio.gather(*tasks)
