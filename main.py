from loguru import logger

from telebot.custom_filters import StateFilter

from loader import bot
import handlers
from utils.set_bot_commands import set_default_commands

logger.add("bot.log", format="{time} {level} {message}", level="DEBUG")

if __name__ == '__main__':
    bot.add_custom_filter(StateFilter(bot))
    set_default_commands(bot)
    bot.infinity_polling()
