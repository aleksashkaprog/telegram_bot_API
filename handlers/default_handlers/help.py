import datetime

from telebot.types import Message

from botrequests.history import update_history_db
from config_data.config import DEFAULT_COMMANDS
from loader import bot
from main import logger


@bot.message_handler(commands=['help'])
def bot_help(message: Message):
    logger.debug(f"Пользователь {message.from_user.id} отправил команду help")
    text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]
    bot.reply_to(message, '\n'.join(text))
    us_id = message.from_user.id
    us_name = message.from_user.username
    update_history_db(us_id, us_name, 'no', message.text, datetime.datetime.now())

