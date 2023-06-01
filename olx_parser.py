import asyncio
from config import load_config
from aiogram.fsm.storage.redis import RedisStorage, Redis
from client_handlers import router, router_price_from, router_price_to, router_district
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

'''
This version utilizes aiogram. 
In the current version  of the script the parameters are obtained via Telegram chat from the user to generate a 
url for further parsing and sending the info back to the user. More parameters are to be added.
'''
async def set_main_menu(bot):
    main_menu_commands = [
        BotCommand(command='/start',
                   description='О боте'),

        BotCommand(command='/fill',
                   description='Заполнить параметры поиска'),
        BotCommand(command='/alter',
                   description='Изменить параметры поиска'),
        BotCommand(command='/alter',
                   description='Изменить параметры поиска'),
        BotCommand(command='/alter',
                   description='Изменить параметры поиска'),
        BotCommand(command='/alter',
                   description='Изменить параметры поиска'),
        BotCommand(command='/show',
                   description='Параметры поиска сейчас'),
    ]
        await bot.set_my_commands(main_menu_commands)

async def main():
    print('Бот недвига вышел в онлайн')

    config = load_config(None)
    bot: Bot = Bot(token=config.tg_bot.token)
    redis: Redis = Redis(host='localhost')
    storage: RedisStorage = RedisStorage(redis=redis)
    dp: Dispatcher = Dispatcher(storage=storage)
    dp.include_routers(router,
                       router_price_from,
                       router_price_to,
                       router_district)
    # dp.include_router(router_price_from)
    # dp.include_router(router_price_to)
    # dp.include_router(router_district)
    # dp.include_router()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())









