from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage # Might be absent in the current version
from decouple import config
from database import Database


#storage: MemoryStorage = MemoryStorage() # TODO: how do we use Memory storage here?
bot = Bot(token=config('bot_token'))
dp = Dispatcher() #(storage=storage)
db = Database(db_path='DB/realty5.db')

db.del_db_content()