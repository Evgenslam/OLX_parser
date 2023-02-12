import time
import sqlite3
import requests
from datetime import datetime
from typing import Dict, List
from bs4 import BeautifulSoup
from decouple import config

# for using fake useragent
# ua = fake_useragent.UserAgent(verify_ssl=False)  # с фейковым юзерагентом почему-то не работает

# for proxy rotation
#proxy_list: dict = config('proxy_list')
start_time: float = time.time()

my_headers: dict = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
}


def get_cards(url: str, payload: dict) -> List[str]:
    '''
    This function extracts individual ad cards using BeautifulSoup
    '''
    # headers = {'User-Agent': ua.random}  # фейковый юзерагент почему-то не работает
    # random_proxy = choice(proxy_list)
    # proxies = {'http': 'http://' + random_proxy}
    try:
        # print(f'Using proxy {random_proxy}')
        response = requests.get(url=url, headers=my_headers, params=payload)  # , proxies=proxies
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        cards = [x for x in soup.find_all('div', {"data-cy": "l-card"}) if
                 'ТОП' not in x.text]
    except requests.exceptions.Timeout:
        print("Timeout occurred")
        print(f'Жопа наступила в {time.ctime(time.time())}')
    return cards


def get_offer(card: str, districts: List[str]) -> Dict[str, str]:
    """
    This parser function extracts name, price, district, date and time as well ass link from an individual ad card
    """
    offer: dict = {}
    loctime = card.find('p', {'data-testid': 'location-date'}).text
    district = loctime.split(' - ')[0].split()[1]  # lstrip('Ташкент, ').rstrip(' район')
    current_date = str(datetime.now().date())
    if not districts or district in districts:
        offer["title"] = card.find('h6').text
        offer["price"] = card.find('p', {'data-testid': 'ad-price'}).text
        offer["district"] = district
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


