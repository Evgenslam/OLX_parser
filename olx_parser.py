import time
from random import randint
from typing import List

import requests
from bs4 import BeautifulSoup
from decouple import config

from check_database import check_database

my_headers: dict = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
}
# ua = fake_useragent.UserAgent(verify_ssl=False)  # с фейковым юзерагентом почему-то не работает

'''
In the current version of the script we just copy the URL after making our query by hands directly at the site.
In the future the parameters will be obtained via Telegram chat from the user and inserted into the script.
'''
# params = {
#     'currency': 'UZS',
#     'search[filter_enum_comission][0]': 'no'
# }

#proxy_list: dict = config('proxy_list')


def get_cards(url: str) -> List[str]:
    '''
    This function extracts individual ad cards using BeautifulSoup
    '''
    # headers = {'User-Agent': ua.random}  # фейковый юзерагент почему-то не работает
    # random_proxy = choice(proxy_list)
    # proxies = {'http': 'http://' + random_proxy}
    try:
        # print(f'Using proxy {random_proxy}')
        response = requests.get(url=url, headers=my_headers)  # , proxies=proxies
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        cards = [x for x in soup.find_all('div', {"data-cy": "l-card"}) if
                 'ТОП' not in x.text]
    except requests.exceptions.Timeout:
        print("Timeout occurred")
        print(f'Жопа наступила в {time.ctime(time.time())}')
    return cards


def get_offers(cards: List[str]) -> None:
    '''
    This function iterates through ad cards using another function (check_database)
    '''
    for card in cards:
        check_database(card)


def main():
    while True:
        cards: List[str] = get_cards(url=config('url'))
        get_offers(cards)
        time.sleep(randint(120, 180))


if __name__ == "__main__":
    main()
