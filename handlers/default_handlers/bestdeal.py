import datetime

from telebot.types import Message, ReplyKeyboardRemove, CallbackQuery
from telebot import types

from botrequests.bestdeal import get_bestdeal
from botrequests.common_requests import find_city, find_destinationid
from botrequests.history import update_history_db
from keyboards.reply.reply import keyboard_city, keyboard_yesno, keyboard_number
from loader import bot
from telegram_bot_calendar.base import LSTEP
from telegram_bot_calendar.detailed import DetailedTelegramCalendar

from my_calendar import get_calendar, calendar_command, ALL_STEPS
from states.best_info import BestInfoState


@bot.message_handler(commands=['bestdeal'])
def bot_bestdeal(message: Message):
    bot.send_message(message.from_user.id, 'Введите город, в который хотите поехать')
    bot.register_next_step_handler(message, check_city)



def check_city(message):
    bot.set_state(message.from_user.id, BestInfoState.city_id, message.chat.id)
    bot.send_message(message.from_user.id, text='Выберите город', reply_markup=keyboard_city(message.text))
    bot.register_next_step_handler(message, calendar_command)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=5))
def check_in_date(call: CallbackQuery) -> None:
    today = datetime.date.today()
    result, key, step = get_calendar(calendar_id=1,
                                     current_date=today,
                                     min_date=today,
                                     max_date=today + datetime.timedelta(days=365),
                                     locale="ru",
                                     is_process=True,
                                     callback_data=call)
    if not result and key:
        bot.edit_message_text(f"Выберите {ALL_STEPS[step]}",
                              call.from_user.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['checkin_date'] = result

            bot.edit_message_text(f"Дата заезда {result}",
                                  call.message.chat.id,
                                  call.message.message_id)

            bot.send_message(call.from_user.id, "Выберите дату выезда")
            calendar, step = get_calendar(calendar_id=2,
                                          min_date=result + datetime.timedelta(days=1),
                                          max_date=result + datetime.timedelta(days=365),
                                          locale="ru",
                                          )

            bot.send_message(call.from_user.id,
                             f"Выберите {ALL_STEPS[step]}",
                             reply_markup=calendar)

        bot.set_state(call.from_user.id, BestInfoState.checkout_date, call.message.chat.id)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=6))
def check_out_date(call: CallbackQuery) -> None:
    today = datetime.date.today()
    result, key, step = get_calendar(calendar_id=2,
                                     current_date=today,
                                     min_date=today,
                                     max_date=today + datetime.timedelta(days=365),
                                     locale="ru",
                                     is_process=True,
                                     callback_data=call)
    if not result and key:
        bot.edit_message_text(f"Выберите {ALL_STEPS[step]}",
                              call.from_user.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['checkout_date'] = result

            bot.edit_message_text(f"Дата выезда {result}",
                                  call.message.chat.id,
                                  call.message.message_id)


def hotels_count(message):
    bot.set_state(message.from_user.id, BestInfoState.hotels_count, message.chat.id)
    bot.send_message(message.from_user.id, text='Сколько отелей Вы хотите посмотреть?',
                     reply_markup=keyboard_number())
    bot.register_next_step_handler(message, low)


def low(message):
    bot.set_state(message.from_user.id, BestInfoState.low_price, message.chat.id)
    bot.send_message(message.from_user.id, 'Укажите самую дешевую цену, устраивающую вас',
                     reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(message, high)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['hotels_count'] = message.text


def high(message):
    bot.set_state(message.from_user.id, BestInfoState.high_price, message.chat.id)
    bot.send_message(message.from_user.id, 'Укажите самую дорогую цену, устраивающую вас')
    bot.register_next_step_handler(message, min)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['low_price'] = message.text


def min(message):
    bot.set_state(message.from_user.id, BestInfoState.min_distance, message.chat.id)
    bot.send_message(message.from_user.id, 'Укажите минимально расстояние до центра, устраивающее вас')
    bot.register_next_step_handler(message, max)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['high_price'] = message.text


def max(message):
    bot.set_state(message.from_user.id, BestInfoState.max_distance, message.chat.id)
    bot.send_message(message.from_user.id, 'Укажите максимальное расстояние до центра, устраивающее вас')
    bot.register_next_step_handler(message, is_photos)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['min_distance'] = message.text


def is_photos(message):
    bot.send_message(message.from_user.id, text='Хотите ли Вы посмотреть фотографии отелей?', reply_markup=keyboard_yesno())
    bot.register_next_step_handler(message, get_info)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['max_distance'] = message.text


def get_info(message):
    history_string = ''
    if message.text.lower() == 'нет':
        bot.send_message(message.from_user.id, 'Подождите немного, Ваш запрос обрабатывается',
                         reply_markup=ReplyKeyboardRemove())
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            for i in get_bestdeal(city_id=find_destinationid(data['city_id']), low_price=int(data['low_price']),
                                  high_price=int(data['high_price']),
                                  min_distance=float(data['min_distance']), max_distance=float(data['max_distance']),
                                  hotels_count=int(data['hotels_count']), checkin_date=data['chekin_date'],
                                  checkout_date=data['checkout_date'], count_photo=0):
                bot.send_message(message.from_user.id, i)
                history_string += i
        us_id = message.from_user.id
        us_name = message.from_user.username
        update_history_db(us_id, us_name, history_string, '/bestdeal', datetime.datetime.now())

    elif message.text.lower() == 'да':
        bot.set_state(message.from_user.id, BestInfoState.count_photo, message.chat.id)
        bot.send_message(message.from_user.id, text='Сколько фотографий Вы хотите посмотреть?', reply_markup=keyboard_number())
        bot.register_next_step_handler(message, get_info_with_photo)


def get_info_with_photo(message):
    history_string = ''
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['count_photo'] = message.text
    bot.send_message(message.from_user.id, 'Подождите немного, Ваш запрос обрабатывается',
                     reply_markup=ReplyKeyboardRemove())
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        for i in get_bestdeal(city_id=find_destinationid(data['city_id']), low_price=int(data['low_price']),
                              high_price=int(data['high_price']),
                              min_distance=float(data['min_distance']), max_distance=float(data['max_distance']),
                              hotels_count=int(data['hotels_count']), checkin_date=data['chekin_date'],
                              checkout_date=data['checkout_date'], count_photo=int(data['count_photo'])):
            bot.send_message(message.from_user.id, i)
            history_string += i
    us_id = message.from_user.id
    us_name = message.from_user.username
    update_history_db(us_id, us_name, history_string, '/bestdeal', datetime.datetime.now())

