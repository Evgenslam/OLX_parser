from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from decouple import config
from database import Database


storage: MemoryStorage = MemoryStorage() # TODO: how do we use Memory storage here?
bot = Bot(token=config('bot_token'))
dp = Dispatcher(bot, storage=storage)
db = Database(db_path='DB/realty5.db')

db.del_db_content()