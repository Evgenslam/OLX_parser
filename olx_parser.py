from typing import List
from decouple import config
from module import get_cards, check_database

'''
This version utilizes check_database function (includes check_db, send_telegram, send_db)
In the current version of the script we just copy the URL after making our query by hands directly at the site.
In the future the parameters will be obtained via Telegram chat from the user and inserted into the script.
'''


def main():
    while True:
        cards: List[str] = get_cards(url=config('url'))
        for card in cards:
            check_database(card)


if __name__ == "__main__":
    main()
# TEST