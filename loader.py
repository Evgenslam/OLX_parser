from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, Redis
from decouple import config
from database import Database


redis: Redis = Redis(host='localhost')
storage: RedisStorage = RedisStorage(redis=redis)
bot: Bot = Bot(token=config('bot_token'))
dp: Dispatcher = Dispatcher(storage=storage)
db = Database(db_path='DB/realty5.db')

db.del_db_content()