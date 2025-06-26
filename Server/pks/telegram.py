import requests
import logging
import random

from .config import Config


class TelegramBot:


    def __init__(self):
        self.__set_identifier()
        logging.info(f"New instance \"{self.identifier}\" of the Telegram bot created.")
        self.__set_token()
        # Construct API address
        self.api_url = f"https://api.telegram.org/bot{self.token}/"
        if not self.__is_token_valid():
            raise ValueError("The Telegram token is invalid. Please check config.py.")

    def __del__(self):
        logging.info(f"Bot instance {self.identifier} destroyed.")

    def __set_identifier(self) -> None:
        
        identifier = ''.join([(chr(random.randint(97, 123))) for _ in range(6)])
        self.identifier = identifier[0].upper() + identifier[1:]

    def __set_token(self) -> None:
        
        self.token = Config.telegram_token

    def __is_token_valid(self) -> bool:
        
        r = requests.get(self.api_url)
        if r.json()["description"] != "Not Found":  # The API returns "Unauthorized" when the token is invalid.
            return False
        return True

    def get_updates(self, offset: int = 0, timeout: int = 30) -> dict:
        
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id: str, text: str, reply_to: str or None = None) -> requests.Response:
        
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}

        if type(reply_to) == int:
            params.update({"reply_to_message_id": reply_to})

        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp
