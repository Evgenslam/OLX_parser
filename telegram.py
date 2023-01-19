import requests


class Telegram:

    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    def send_telegram(self, text):
        data = dict(chat_id=self.chat_id, text=text, parse_mode='HTML')
        response = requests.post(url=self.url, data=data)
        print(response)