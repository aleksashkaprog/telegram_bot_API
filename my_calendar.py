import datetime

from TelegramBotAPI.types import Message
from telebot.types import CallbackQuery
from telegram_bot_calendar import DetailedTelegramCalendar

from loader import bot
from states.best_info import BestInfoState
from states.low_and_high_price_info import HotelInfoState


def get_calendar(is_process=False, callback_data=None, **kwargs):
    if is_process:
        result, key, step = DetailedTelegramCalendar(calendar_id=kwargs['calendar_id'],
                                                     current_date=kwargs.get('current_date'),
                                                     min_date=kwargs['min_date'],
                                                     max_date=kwargs['max_date'],
                                                     locale=kwargs['locale']).process(callback_data.data)
        return result, key, step
    else:
        calendar, step = DetailedTelegramCalendar(calendar_id=kwargs['calendar_id'],
                                                  current_date=kwargs.get('current_date'),
                                                  min_date=kwargs['min_date'],
                                                  max_date=kwargs['max_date'],
                                                  locale=kwargs['locale']).build()
        return calendar, step

ALL_STEPS = {'y': 'год', 'm': 'месяц', 'd': 'день'}
@bot.message_handler(commands=['calendar'])
def calendar_command(message: Message):
    today = datetime.date.today()
    calendar, step = get_calendar(calendar_id=1,
                                  current_date=today,
                                  min_date=today,
                                  max_date=today + datetime.timedelta(days=365),
                                  locale="ru")

    bot.set_state(message.from_user.id, BestInfoState.checkin_date, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['city_id'] = message.text
    bot.send_message(message.from_user.id, f"Выберите дату заезда, {ALL_STEPS[step]}", reply_markup=calendar)




