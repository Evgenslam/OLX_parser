# Правки и коменты можно вносить сюда


from bs4 import BeautifulSoup
import requests
import sqlite3
from config import bot_token, chat_id
from datetime import datetime
import fake_useragent
from random import randint, choice
import time

start_time = time.time()

my_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
}

ua = fake_useragent.UserAgent(verify_ssl=False)  # с фейковым юзерагентом почему-то не работает

'''
Сейчас вбиваем нужный запрос, затем передаём ссылку в скрипт. 
В будущем можно будет запрашивать параметры в телеге и подставлять их сюда.
'''
# params = {
#     'currency': 'UZS',
#     'search[filter_enum_comission][0]': 'no'
# }


with open('spaceproxies.txt', 'r') as f:  #получаем список прокси для ротации из отдельного файла
    proxy_list = f.read().split('\n')


def format_text(offer):
    text = f"""{offer['price']}
    {offer['district']}
    {offer['lnk']}
    {offer['title']}
    {offer['time']}"""
    return text


def send_telegram(offer):
    text = format_text(offer)
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
    }
    response = requests.post(url=url, data=data)
    print(response)


def get_cards(url):  # функция вытаскивает карточки объявлений со страницы красивым супом
    #headers = {'User-Agent': ua.random}  # фейковый юзерагент почему-то не работает
    random_proxy = choice(proxy_list)
    proxies = {'http': 'http://' + random_proxy}
    try:
        print(f'Using proxy {random_proxy}')
        response = requests.get(url=url, headers=my_headers, proxies=proxies)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        cards = [x for x in soup.find_all('div', {"data-cy": "l-card"}) if 'ТОП' not in x.text]
    except requests.exceptions.Timeout:
        print("Timeout occurred")
        print(f'Жопа наступила в {time.ctime(time.time())}')
    return cards

'''
Функция проверяет, есть ли объява в БД, если нет, а) присылает её в телегу б) добавляет в БД в)делает принты
'''
def check_database(card):
    title = card.find('h6').text
    with sqlite3.connect('realty4.db') as connection:
        cursor = connection.cursor()
        cursor.execute('''
            SELECT title FROM offers WHERE title = (?)
        ''', (title, ))
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


def get_offer(card):  #функция-парсер для одного объявления, извлекает название, цену, район, дату, времы, ссылку
    offer = {}
    loctime = card.find('p', {'data-testid': 'location-date'}).text
    current_date = str(datetime.now().date())
    offer["title"] = card.find('h6').text
    offer["price"] = card.find('p', {'data-testid': 'ad-price'}).text
    offer["district"] = loctime.split(' - ')[0].lstrip('Ташкент, ')
    offer["time"] = loctime.split(' - ')[1].replace('Сегодня', current_date)
    offer["lnk"] = 'https://www.olx.uz/' + card.find('a')['href']
    return offer


def get_offers(cards):  #функция прогоняет все найденные карточки объявлений через проверку на наличие в БД и т.д.
    for card in cards:
        check_database(card)


def main():
    while True:
        cards = get_cards(url='https://www.olx.uz/d/nedvizhimost/kvartiry/arenda-dolgosrochnaya/tashkent/?currency=UZS&search%5Border%5D=created_at%3Adesc&search%5Bfilter_enum_comission%5D%5B0%5D=no&view=list')
        get_offers(cards)
        time.sleep(randint(120, 180))

if __name__ == "__main__":
    main()

