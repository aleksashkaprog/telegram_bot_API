import datetime

from telebot.types import Message

from botrequests.history import get_history_db, update_history_db
from loader import bot
from main import logger


@bot.message_handler(commands=['history'])
def bot_history(message: Message):
    logger.debug(f"Пользователь {message.from_user.id} отправил команду history")
    for his in get_history_db(message.from_user.username):
        bot.send_message(message.from_user.id, his)
    us_id = message.from_user.id
    us_name = message.from_user.username
    update_history_db(us_id, us_name, 'no', message.text, datetime.datetime.now())


