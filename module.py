import time
import sqlite3
import requests
from random import randint
from datetime import datetime
from typing import Dict, List
from bs4 import BeautifulSoup
from decouple import config
from functools import reduce
from operator import add

# for using fake useragent
# ua = fake_useragent.UserAgent(verify_ssl=False)  # с фейковым юзерагентом почему-то не работает

# for shortening URL
# params = {
#     'currency': 'UZS',
#     'search[filter_enum_comission][0]': 'no'
# }

# for proxy rotation
#proxy_list: dict = config('proxy_list')
start_time: float = time.time()

my_headers: dict = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
}


def ask_parameters() -> tuple:
    district_targ = input('В каком районе хотели бы снять квартиру: ')  # проверка в БД
    rooms_targ = input('Сколько комнат: ')
    price_targ = input('Максимальная стоимость в сумах, которую вы готовы заплатить: ')
    commision_targ = input(
        'Готовы ли вы рассматривать варианты с комиссией (да/нет): ')  # проверка в параметрах и БД
    area_from_targ = input('Площадь от: ')
    area_to_targ = input('Площадь до: ')
    return '', '', price_targ, rooms_targ, ['no', 'yes'][commision_targ == 'да'], area_from_targ, area_to_targ, '', \
                                                                          district_targ

# my_params = ('', '', '600000', '2', 'no', '40', '60', '', 'Чиланзор')
# x_url = config('the_url')
#     for ind, part in enumerate(url_list):
#         print(ind, part)
def make_url(url: str, query_params: tuple) -> str:
    url_list = url.split('&')
    zip_list = list(zip(url_list, query_params))
    the_list = [''.join(x) for x in zip_list]
    ready_url = '&'.join(the_list)
    return ready_url


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


def get_offer(card: str) -> Dict[str, str]:
    """
    This parser function extracts name, price, district, date and time as well ass link from an individual ad card
    """
    offer: dict = {}
    loctime = card.find('p', {'data-testid': 'location-date'}).text
    current_date = str(datetime.now().date())
    offer["title"] = card.find('h6').text
    offer["price"] = card.find('p', {'data-testid': 'ad-price'}).text
    offer["district"] = loctime.split(' - ')[0].lstrip('Ташкент, ')
    offer["time"] = loctime.split(' - ')[1].replace('Сегодня', current_date)
    offer["lnk"] = 'https://www.olx.uz/' + card.find('a')['href']
    return offer


def format_text(offer: Dict[str, str]) -> str:
    '''
    This function formats an offer into text ready for posting in telegram
    '''
    text: str = f"""{offer['price']}
    {offer['district']}
    {offer['lnk']}
    {offer['title']}
    {offer['time']}"""
    return text


def send_telegram(offer: Dict[str, str]) -> None:
    text: str = format_text(offer)
    url: str = f"https://api.telegram.org/bot{config('bot_token')}/sendMessage"
    data: dict = dict(chat_id=config('chat_id'), text=text, parse_mode='HTML')
    response = requests.post(url=url, data=data)
    print(response)


def check_database(card: str) -> None:
    '''
    This function checks if the ad is already in the DB. If it is not, a)sends in to Telegram b)adds it to the DB
    c)makes necessary prints
    '''
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


