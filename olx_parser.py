import asyncio
from client import router
from loader import dp, bot

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
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())









