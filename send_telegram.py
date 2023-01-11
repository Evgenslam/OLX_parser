import requests
from typing import Dict
from decouple import config


def format_text(offer: Dict[str, str]) -> str:
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