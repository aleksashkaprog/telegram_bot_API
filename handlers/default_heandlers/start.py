import datetime

from telebot.types import Message

from botrequests.history import update_history_db
from loader import bot


@bot.message_handler(commands=['start'])
def bot_start(message: Message):
    bot.reply_to(message, f"Здравствуйте, {message.from_user.full_name}!Вас приветствует телеграм-бот турагенства "
                          f"'Too Easy Travel'. Чем я могу помочь Вам?")
    us_id = message.from_user.id
    us_name = message.from_user.username
    update_history_db(us_id, us_name, 'no', message.text, datetime.datetime.now())
