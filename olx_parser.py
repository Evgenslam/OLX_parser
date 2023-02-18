from aiogram.utils import executor
from client import register_handlers
from loader import dp

'''
This version utilizes aiogram. 
In the current version  of the script the parameters are obtained via Telegram chat from the user to generate a 
url for further parsing and sending the info back to the user. More parameters are added in feature branch.
'''


def main():
    async def on_startup(_):
        print('Бот недвига вышел в онлайн')
    register_handlers(dp)
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


if __name__ == "__main__":
    main()









