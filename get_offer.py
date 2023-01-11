from datetime import datetime
from typing import Dict


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
