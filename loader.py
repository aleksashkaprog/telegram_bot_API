from loguru import logger
from telebot import TeleBot

from config_data import config

bot = TeleBot(token=config.BOT_TOKEN)

logger.add("bot.log", format="{time} {level} {message}", level="DEBUG")
