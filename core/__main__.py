from aiogram import Dispatcher
from aiogram.utils import executor

from core.commands import set_default_commands
from loguru import logger

from core.loader import dp


async def startup(disp: Dispatcher) -> None:
    await set_default_commands(dp=disp)
    logger.info("Start bot")


async def shutdown(disp: Dispatcher) -> None:
    logger.info("Bot finished")

if __name__ == '__main__':
    executor.start_polling(
        dispatcher=dp,
        skip_updates=True,
        on_startup=startup,
        on_shutdown=shutdown
    )
