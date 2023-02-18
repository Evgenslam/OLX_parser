from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from decouple import config

storage = MemoryStorage() # TODO: how do we use Memory storage here?
bot = Bot(token=config('bot_token'))
dp = Dispatcher(bot, storage=storage)