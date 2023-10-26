import logging
import betterlogging as bl

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.config import load_config
from tgbot.middlewares.album_mw import AlbumMiddleware
from tgbot.middlewares.config import ConfigMiddleware

config = load_config(".env")
bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
dp = Dispatcher()
scheduler = AsyncIOScheduler()

logger = logging.getLogger(__name__)
log_level = logging.INFO
bl.basic_colorized_config(level=log_level)

DB_URL = config.db.url


def register_global_middlewares(dp: Dispatcher, config):
    dp.message.outer_middleware(ConfigMiddleware(config))
    dp.callback_query.outer_middleware(ConfigMiddleware(config))
    dp.message.outer_middleware(AlbumMiddleware(config))
