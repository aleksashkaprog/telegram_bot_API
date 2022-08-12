import datetime
from datetime import timedelta

from telebot.types import CallbackQuery, Message, ReplyKeyboardRemove
from telegram_bot_calendar import DetailedTelegramCalendar

from botrequests.common_requests import find_destinationid
from botrequests.history import update_history_db
from botrequests.low_and_highprice import find_hotels
from keyboards.reply.reply import (keyboard_city, keyboard_number,
                                   keyboard_yesno)
from loader import bot, logger
from states.low_and_high_price_info import HotelInfoState
from utils.my_calendar import ALL_STEPS, get_calendar


@bot.message_handler(commands=['highprice'])
def bot_highprice(message: Message):
    logger.debug(f"Пользователь {message.from_user.id} отправил команду highprice")
    bot.send_message(message.from_user.id, 'Введите город, в который хотите поехать (латиницей)')
    bot.register_next_step_handler(message, check_city)


def check_city(message):
    bot.set_state(message.from_user.id, HotelInfoState.city_id, message.chat.id)
    bot.send_message(message.from_user.id, text='Выберите город', reply_markup=keyboard_city(message.text))
    bot.register_next_step_handler(message, calendar_command)

@bot.message_handler(commands=['calendar'])
def calendar_command(message: Message):
    logger.debug(f"Пользователь {message.from_user.id} выбрал город {message.text}")
    today = datetime.date.today()
    calendar, step = get_calendar(calendar_id=3,
                                  current_date=today,
                                  min_date=today,
                                  max_date=today + datetime.timedelta(days=365),
                                  locale="ru")

    bot.set_state(message.from_user.id,HotelInfoState.checkin_date, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['city_id'] = message.text
    bot.send_message(message.from_user.id, f"Выберите дату заезда, {ALL_STEPS[step]}", reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=3))
def check_in_date(call: CallbackQuery) -> None:
    today = datetime.date.today()
    result, key, step = get_calendar(calendar_id=3,
                                     current_date=today,
                                     min_date=today,
                                     max_date=today + timedelta(days=365),
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
            calendar, step = get_calendar(calendar_id=4,
                                          min_date=result + datetime.timedelta(days=1),
                                          max_date=result + datetime.timedelta(days=365),
                                          locale="ru",
                                          )

            bot.send_message(call.from_user.id,
                             f"Выберите {ALL_STEPS[step]}",
                             reply_markup=calendar)

        bot.set_state(call.from_user.id, HotelInfoState.checkout_date, call.message.chat.id)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=4))
def check_out_date(call: CallbackQuery) -> None:
    today = datetime.date.today()
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        result, key, step = get_calendar(calendar_id=4,
                                         current_date=today,
                                         min_date=data['checkin_date'] + timedelta(days=1),
                                         max_date=data['checkin_date'] + timedelta(days=365),
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

            bot.edit_message_text(f"Дата выезда {result}. Напишите ok для продолжения",
                                  call.message.chat.id,
                                  call.message.message_id)
            bot.register_next_step_handler(call.message, hotels_count)


def hotels_count(message):
    logger.debug(f"Пользователь {message.from_user.id} выбрал даты заезда и выезда")
    bot.set_state(message.from_user.id, HotelInfoState.hotels_count, message.chat.id)
    bot.send_message(message.from_user.id, text='Сколько отелей Вы хотите посмотреть?',
                     reply_markup=keyboard_number())
    bot.register_next_step_handler(message, is_photos)


def is_photos(message):
    logger.debug(f"Пользователь {message.from_user.id} выбрал количество отелей")
    bot.send_message(message.from_user.id, text='Хотите ли Вы посмотреть фотографии отелей?',
                     reply_markup=keyboard_yesno())
    bot.register_next_step_handler(message, get_info)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['hotels_count'] = message.text


def get_info(message):
    history_string = ''
    if message.text.lower() == 'нет':
        bot.send_message(message.from_user.id, 'Подождите немного, Ваш запрос обрабатывается',
                         reply_markup=ReplyKeyboardRemove())
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            for i in find_hotels(city_id=find_destinationid(data['city_id']), hotels_count=int(data['hotels_count']),
                                 checkin_date=data['checkin_date'], checkout_date=data['checkout_date'], sortOrder="PRICE_HIGHEST_FIRST",
                                 count_photo=0):
                bot.send_message(message.from_user.id, i)
                history_string += i
        us_id = message.from_user.id
        us_name = message.from_user.username
        update_history_db(us_id, us_name, history_string, '/highprice', datetime.datetime.now())
        logger.debug(f"Пользователь {message.from_user.id} получил информацию по команде highprice без фото")

    elif message.text.lower() == 'да':
        bot.set_state(message.from_user.id, HotelInfoState.count_photo, message.chat.id)
        bot.send_message(message.from_user.id, text='Сколько фотографий Вы хотите посмотреть?',
                         reply_markup=keyboard_number())
        bot.register_next_step_handler(message, get_info_with_photo)


def get_info_with_photo(message):
    logger.debug(f"Пользователь {message.from_user.id} выбрал количество фото")
    history_string = ''
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['count_photo'] = message.text
    bot.send_message(message.from_user.id, 'Подождите немного, Ваш запрос обрабатывается',
                     reply_markup=ReplyKeyboardRemove())
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        for i in find_hotels(city_id=find_destinationid(data['city_id']), hotels_count=int(data['hotels_count']),
                             checkin_date=data['checkin_date'], checkout_date=data['checkout_date'], sortOrder="PRICE_HIGHEST_FIRST",
                             count_photo=int(data['count_photo'])):
            bot.send_message(message.from_user.id, i)
            history_string += i
    us_id = message.from_user.id
    us_name = message.from_user.username
    update_history_db(us_id, us_name, history_string,'/highprice', datetime.datetime.now())
    logger.debug(f"Пользователь {message.from_user.id} получил информацию по команде highprice с фото")
