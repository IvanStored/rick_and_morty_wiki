from aiogram import Dispatcher
from aiogram import types


async def set_default_commands(dp: Dispatcher) -> None:
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Start bot"),
            types.BotCommand("all_characters", "All characters"),
            types.BotCommand("all_locations", "All locations"),
            types.BotCommand("all_episodes", "All episodes")
        ]
    )