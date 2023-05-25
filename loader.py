# from aiogram import Bot, Dispatcher
# from aiogram.fsm.storage.redis import RedisStorage, Redis
# from environs import Env
from database import Database

# env = Env()
# env.read_env()
#
# redis: Redis = Redis(host='localhost')
# storage: RedisStorage = RedisStorage(redis=redis)
# bot: Bot = Bot(token=env('BOT_TOKEN'))
# dp: Dispatcher = Dispatcher(storage=storage)
db = Database(db_path='DB/realty5.db')
db.del_db_content()