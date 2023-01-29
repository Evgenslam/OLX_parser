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
url = make_url(config('the_url'), query_params)


def main():
    while True:
        db = Database(db_path='DB/realty4.db')
        cards: List[str] = get_cards(url=url)
        for card in cards:
            if not db.check_entry(card):
                offer = get_offer(card)
                text = format_text(offer)
                tg.send_telegram(text)
                db.send_to_db(offer)

        time.sleep(randint(30, 40))
        # # count = 0
        # #     count += 1
        # # print(count)
        # # print('=' * 30, f'\n{len(cards)}: {len(set(cards))}')
        # # break


if __name__ == "__main__":
    main()
