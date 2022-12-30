# Правки и коменты можно вносить сюда

import sqlite3
import time
from datetime import datetime
from random import randint
from typing import List, Dict

import requests
from bs4 import BeautifulSoup
from decouple import config

# import pydantic
# from typing import Optional

start_time: float = time.time()

my_headers: dict = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
}
# ua = fake_useragent.UserAgent(verify_ssl=False)  # с фейковым юзерагентом почему-то не работает

'''
Сейчас вбиваем нужный запрос, затем передаём ссылку в скрипт.
В будущем можно будет запрашивать параметры в телеге и подставлять их сюда.
'''
# params = {
#     'currency': 'UZS',
#     'search[filter_enum_comission][0]': 'no'
# }

proxy_list: dict = config('proxy_list')


def format_text(offer: Dict[str]) -> str:
    text: str = f"""{offer['price']}
    {offer['district']}
    {offer['lnk']}
    {offer['title']}
    {offer['time']}"""
    return text


def send_telegram(offer: Dict[str]) -> None:
    text: str = format_text(offer)
    url: str = f"https://api.telegram.org/bot{config('bot_token')}/sendMessage"
    data: dict = {'chat_id': config('chat_id'),
            'text': text,
            'parse_mode': 'HTML'
            }
    response = requests.post(url=url, data=data)
    print(response)


def get_cards(url: str) -> List[str]:  # функция вытаскивает карточки объявлений со страницы красивым супом
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


'''
Функция проверяет, есть ли объява в БД, если нет, а) присылает её в телегу б) добавляет в БД в)делает принты
'''


def check_database(card: str) -> None:
    title: str = card.find('h6').text
    with sqlite3.connect('DB/realty4.db') as connection:
        cursor = connection.cursor()
        cursor.execute('''
            SELECT title FROM offers WHERE title = (?)
        ''', (title,))
        result = cursor.fetchone()
        if result is None:
            offer = get_offer(card)
            send_telegram(offer)
            cursor.execute('''
                INSERT INTO offers
                VALUES(NULL, :title, :price, :district, :time, :lnk)
            ''', offer)
            connection.commit()
            print(f'●Объявление ---{title}--- добавлено в базу данных')
            print(f'Время добавления в базу данных: {time.ctime(time.time())}')
            print(f'Время с начала запуска скрипта: {time.time() - start_time}')


def get_offer(card: str) -> Dict[str]:  # функция-парсер для одного объявления, извлекает название, цену, район, дату,
    # время, ссылку
    offer: dict = {}
    loctime = card.find('p', {'data-testid': 'location-date'}).text
    current_date = str(datetime.now().date())
    offer["title"] = card.find('h6').text
    offer["price"] = card.find('p', {'data-testid': 'ad-price'}).text
    offer["district"] = loctime.split(' - ')[0].lstrip('Ташкент, ')
    offer["time"] = loctime.split(' - ')[1].replace('Сегодня', current_date)
    offer["lnk"] = 'https://www.olx.uz/' + card.find('a')['href']
    return offer


def get_offers(cards: List[str]) -> None:  # функция прогоняет все найденные карточки объявлений через проверку на
    # наличие в БД и т.д.
    for card in cards:
        check_database(card)


def main():
    while True:
        cards: List[str] = get_cards(url=config('url'))
        get_offers(cards)
        time.sleep(randint(120, 180))


if __name__ == "__main__":
    main()
