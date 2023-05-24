import asyncio
from config import load_config
from aiogram.fsm.storage.redis import RedisStorage, Redis
from client_handlers import router, router_district
from aiogram import Bot, Dispatcher
from database import Database

'''
This version utilizes aiogram. 
In the current version  of the script the parameters are obtained via Telegram chat from the user to generate a 
url for further parsing and sending the info back to the user. More parameters are added in feature branch.
'''
# async def set_main_menu(bot):
#     main_menu_commands = [
#         BotCommand(command='/see_my_params',
#                    description='Параметры поиска сейчас'),
#         BotCommand(command='/change_my_params',
#                    description='Изменить параметры поиска')]
#         await bot.set_my_commands(main_menu_commands)

async def main():
    print('Бот недвига вышел в онлайн')

    config = load_config(None)
    bot: Bot = Bot(token=config.tg_bot.token)
    redis: Redis = Redis(host='localhost')
    storage: RedisStorage = RedisStorage(redis=redis)
    dp: Dispatcher = Dispatcher(storage=storage)
    db = Database(db_path='DB/realty5.db')

    db.del_db_content()
    dp.include_router(router)
    dp.include_router(router_district)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())









