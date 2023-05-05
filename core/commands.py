from aiogram import Dispatcher
from aiogram import types


async def set_default_commands(dp: Dispatcher) -> None:
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Start bot"),
            types.BotCommand("all_characters", "All characters"),
            types.BotCommand(
                "random_character", "Info about random character"
            ),
            types.BotCommand("random_location", "Info about random location"),
        ]
    )
