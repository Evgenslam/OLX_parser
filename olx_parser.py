from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from decouple import config
from aiogram.utils import executor
from client import register_handlers

'''
This version utilizes aiogram.
In the current version  of the script the parameters are obtained via Telegram chat from the user to generate a 
url for further parsing and sending the info back to the user.
'''

storage = MemoryStorage() # TODO: do we actually need Memory storage here?
bot = Bot(token=config('bot_token'))
dp = Dispatcher(bot, storage=storage)


def main():

    async def on_startup(_):
        print('Бот недвига вышел в онлайн')
    register_handlers(dp)
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
    
if __name__ == "__main__":
    main()









