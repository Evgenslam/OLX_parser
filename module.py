import time
import sqlite3
import requests
from datetime import datetime
from typing import Dict, List
from bs4 import BeautifulSoup
from decouple import config
from lexicon_ru import LEXICON_RU

# for using fake useragent
# ua = fake_useragent.UserAgent(verify_ssl=False)  # с фейковым юзерагентом почему-то не работает

# for proxy rotation
#proxy_list: dict = config('proxy_list')
start_time: float = time.time()

my_headers: dict = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
}


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
        print(len(cards))
    except requests.exceptions.Timeout:
        print("Timeout occurred")
        print(f'Жопа наступила в {time.ctime(time.time())}')
    return cards


def get_offer(card: str, search_districts: List[str]) -> Dict[str, str]:
    """
    This parser function extracts name, price, district, date and time as well ass link from an individual ad card
    """
    offer: dict = {}
    loctime = card.find('p', {'data-testid': 'location-date'}).text
    district = loctime.split(' - ')[0].split(',')[1][:-6].lstrip()    # TODO: ugly as fuck, rewrite plz
    print(f'Ищем по районам: {search_districts}')
    print(f'Район в этой карточке: {district}')
    current_date = str(datetime.now().date())
    if not search_districts or district in search_districts:
        offer["название"] = card.find('h6').text
        offer["цена"] = card.find('p', {'data-testid': 'ad-price'}).text
        offer["район"] = district
        offer["время_публикации"] = loctime.split(' - ')[1].replace('Сегодня', current_date)
        offer["ссылка"] = 'https://www.olx.uz/' + card.find('a')['href'] # TODO: make a shorter link
    return offer


def format_text(offer: Dict[str, str]) -> str:
    '''
    This function formats an offer into text ready for posting in telegram
    '''
    # TODO: fix indents for better UX (see Stepik course)
    text: str = f"""{offer['цена']}
    {offer['район']}
    {offer['ссылка']}
    {offer['название']}
    {offer['время_публикации']}"""
    return text


def convert_params(params: dict) -> str:
    trans_dict = {
        'минимальная цена': 'search[filter_float_price:from]',
        'максимальная цена': 'search[filter_float_price:to]',
        'районы': 'districts'
    } # TODO: move the trans_dict into a separate LEXICON file
    ru_params = {ru_param: params.get(trans_dict[ru_param])for ru_param in trans_dict}
    ru_params['районы'] = ', '.join([LEXICON_RU[district] for district in ru_params['районы']])
    ru_params_dict = [f'{key} : {int(val/11420)} $' if type(val) == int
                      else f'{key} : {val}'
                      for key, val in ru_params.items()]
    ru_params_str = '\n'.join(ru_params_dict)
    return ru_params_str


