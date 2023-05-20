from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from decouple import config
from database import Database


storage: MemoryStorage = MemoryStorage() # TODO: how do we use Memory storage here?
bot: Bot = Bot(token=config('bot_token'))
dp: Dispatcher = Dispatcher(storage=storage)
db = Database(db_path='DB/realty5.db')

db.del_db_content()