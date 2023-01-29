import time
from random import randint
from typing import List
from decouple import config
from module import ask_parameters, make_url, get_cards, get_offer, format_text
from telegram import Telegram
from database import Database

'''
This version utilizes classes Database and Telegram
In the current version of the script we generate url using parameters passed by the user via input().
In the future the parameters will be obtained via Telegram chat from the user and inserted into the script.
'''
tg = Telegram(bot_token=config('bot_token'), chat_id=config('chat_id'))
query_params = ask_parameters()
#my_params = ('', '', '600000', '2', 'no', '40', '60', '', 'Чиланзор')
url = make_url(config('the_url'), query_params)
user_phone = input('Пожалуйста, введите свой номер телефона: ')

def main():
    while True:
        db = Database(db_path='DB/realty5.db') # TODO: add number field
        cards: List[str] = get_cards(url=url)
        for card in cards:
            if not db.is_in_db(card):
                offer = get_offer(card)
                offer['user_phone'] = user_phone
                text = format_text(offer)
                db.send_to_db(offer) # TODO: adjust to pass more data
                tg.send_telegram(text) # TODO: Filter by number.Check if having swapped this and previous
                # lines is ok. # TODO: add sent or not field, add field with geenrated  link


        time.sleep(randint(30, 40))
        # # count = 0
        # #     count += 1
        # # print(count)
        # # print('=' * 30, f'\n{len(cards)}: {len(set(cards))}')
        # # break


if __name__ == "__main__":
    main()
