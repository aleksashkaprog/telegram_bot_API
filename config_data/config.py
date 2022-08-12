import os

from dotenv import find_dotenv, load_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
USER_ID = os.getenv('USER_ID')
DEFAULT_COMMANDS = (
    ('start', "Запустить бота"),
    ('help', "Вывести справку"),
    ('lowprice', "Самые дешевые отели"),
    ('highprice', "Самые дорогие отели"),
    ('bestdeal', "Лучшее предложение"),
    ('history', "История поиска")
)
