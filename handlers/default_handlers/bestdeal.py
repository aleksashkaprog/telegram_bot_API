import datetime

from telebot.types import Message, ReplyKeyboardRemove, CallbackQuery

from botrequests.bestdeal import get_bestdeal
from botrequests.common_requests import find_destinationid
from botrequests.history import update_history_db
from keyboards.reply.reply import keyboard_city, keyboard_yesno, keyboard_number
from loader import bot
from main import logger
from telegram_bot_calendar.detailed import DetailedTelegramCalendar

from utils.my_calendar import get_calendar, ALL_STEPS
from states.best_info import BestInfoState


@bot.message_handler(commands=['bestdeal'])
def bot_bestdeal(message: Message):
    logger.debug(f"Пользователь {message.from_user.id} ввел команду bestdeal")
    bot.send_message(message.from_user.id, 'Введите город, в который хотите поехать (латиницей)')
    bot.register_next_step_handler(message, check_city)


def check_city(message):
    bot.set_state(message.from_user.id, BestInfoState.city_id, message.chat.id)
    bot.send_message(message.from_user.id, text='Выберите город', reply_markup=keyboard_city(message.text))
    bot.register_next_step_handler(message, calendar_command)


@bot.message_handler(commands=['calendar'])
def calendar_command(message: Message):
    logger.debug(f"Пользователь {message.from_user.id} выбрал город {message.text}")
    today = datetime.date.today()
    calendar, step = get_calendar(calendar_id=5,
                                  current_date=today,
                                  min_date=today,
                                  max_date=today + datetime.timedelta(days=365),
                                  locale="ru")

    bot.set_state(message.from_user.id, BestInfoState.checkin_date, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['city_id'] = message.text
    bot.send_message(message.from_user.id, f"Выберите дату заезда, {ALL_STEPS[step]}", reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=5))
def check_in_date(call: CallbackQuery) -> None:
    today = datetime.date.today()
    result, key, step = get_calendar(calendar_id=5,
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
            calendar, step = get_calendar(calendar_id=6,
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
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        result, key, step = get_calendar(calendar_id=6,
                                         current_date=today,
                                         min_date=data['checkin_date'] + + datetime.timedelta(days=1),
                                         max_date=data['checkin_date'] + datetime.timedelta(days=365),
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
    bot.set_state(message.from_user.id, BestInfoState.hotels_count, message.chat.id)
    bot.send_message(message.from_user.id, text='Сколько отелей Вы хотите посмотреть?',
                     reply_markup=keyboard_number())
    bot.register_next_step_handler(message, low)


def low(message):
    logger.debug(f"Пользователь {message.from_user.id} выбрал количество отелей")
    bot.set_state(message.from_user.id, BestInfoState.low_price, message.chat.id)
    bot.send_message(message.from_user.id, 'Укажите самую дешевую цену, устраивающую вас',
                     reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(message, high)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['hotels_count'] = message.text


def high(message):
    logger.debug(f"Пользователь {message.from_user.id} выбрал самую низкую цену, устраивающую его")
    bot.set_state(message.from_user.id, BestInfoState.high_price, message.chat.id)
    bot.send_message(message.from_user.id, 'Укажите самую дорогую цену, устраивающую вас')
    bot.register_next_step_handler(message, min)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['low_price'] = message.text


def min(message):
    logger.debug(f"Пользователь {message.from_user.id} выбрал самую высокую цену, устраивающую его")
    bot.set_state(message.from_user.id, BestInfoState.min_distance, message.chat.id)
    bot.send_message(message.from_user.id, 'Укажите минимально расстояние до центра, устраивающее вас')
    bot.register_next_step_handler(message, max)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['high_price'] = message.text


def max(message):
    logger.debug(f"Пользователь {message.from_user.id} выбрал минимальное расстояние до центра, устраивающее его")
    bot.set_state(message.from_user.id, BestInfoState.max_distance, message.chat.id)
    bot.send_message(message.from_user.id, 'Укажите максимальное расстояние до центра, устраивающее вас')
    bot.register_next_step_handler(message, is_photos)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['min_distance'] = message.text


def is_photos(message):
    logger.debug(f"Пользователь {message.from_user.id} выбрал максимальное расстояние до центра, устраивающее его")
    bot.send_message(message.from_user.id, text='Хотите ли Вы посмотреть фотографии отелей?',
                     reply_markup=keyboard_yesno())
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
                                  hotels_count=int(data['hotels_count']), checkin_date=data['checkin_date'],
                                  checkout_date=data['checkout_date'], count_photo=0, page_number=1):
                bot.send_message(message.from_user.id, i)
                history_string += i
        us_id = message.from_user.id
        us_name = message.from_user.username
        update_history_db(us_id, us_name, history_string, '/bestdeal', datetime.datetime.now())
        logger.debug(f"Пользователь {message.from_user.id} получил информацию по команде bestdeal без фото")

    elif message.text.lower() == 'да':
        bot.set_state(message.from_user.id, BestInfoState.count_photo, message.chat.id)
        bot.send_message(message.from_user.id, text='Сколько фотографий Вы хотите посмотреть?',
                         reply_markup=keyboard_number())
        bot.register_next_step_handler(message, get_info_with_photo)


def get_info_with_photo(message):
    logger.debug(f"Пользователь {message.from_user.id} выбрал количество фотографий")
    history_string = ''
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['count_photo'] = message.text
    bot.send_message(message.from_user.id, 'Подождите немного, Ваш запрос обрабатывается',
                     reply_markup=ReplyKeyboardRemove())
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        for i in get_bestdeal(city_id=find_destinationid(data['city_id']), low_price=int(data['low_price']),
                              high_price=int(data['high_price']),
                              min_distance=float(data['min_distance']), max_distance=float(data['max_distance']),
                              hotels_count=int(data['hotels_count']), checkin_date=data['checkin_date'],
                              checkout_date=data['checkout_date'], count_photo=int(data['count_photo']), page_number=1):
            bot.send_message(message.from_user.id, i)
            history_string += i
    us_id = message.from_user.id
    us_name = message.from_user.username
    update_history_db(us_id, us_name, history_string, '/bestdeal', datetime.datetime.now())
    logger.debug(f"Пользователь {message.from_user.id} получил информацию по команде bestdeal с фото")
