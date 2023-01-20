from typing import List
from decouple import config
from module import get_cards, get_offer, format_text
from telegram import Telegram
from database import Database

'''
This version utilizes classes Database and Telegram
In the current version of the script we just copy the URL after making our query by hands directly at the site.
In the future the parameters will be obtained via Telegram chat from the user and inserted into the script.
'''
tg = Telegram(bot_token=config('bot_token'), chat_id=config('chat_id'))

def main():
    while True:
        db = Database(db_path='DB/realty4.db')

        cards: List[str] = get_cards(url=config('url'))
        count = 0
        for card in cards:
            print(cards)
            count += 1
        print(count)
        print('=' * 30, f'\n{len(cards)}: {len(set(cards))}')
        break
                    # offer = get_offer(card)
            # print(offer)

            # if db.check_entry(card):
            #     offer = get_offer(card)
            #     text = format_text(offer)
            #     tg.send_telegram(text)
            #     db.send_to_db(offer)


if __name__ == "__main__":
    main()
