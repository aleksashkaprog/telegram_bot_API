import datetime

from telebot.types import Message, ReplyKeyboardRemove
from telebot import types

from botrequests.bestdeal import get_bestdeal
from botrequests.common_requests import find_city, find_destinationid
from botrequests.history import update_history_db
from keyboards.reply.reply import keyboard_city, keyboard_yesno, keyboard_number
from loader import bot
from telegram_bot_calendar.base import LSTEP
from telegram_bot_calendar.detailed import DetailedTelegramCalendar

command_list = []


@bot.message_handler(commands=['bestdeal'])
def bot_bestdeal(message: Message):
    bot.send_message(message.from_user.id, 'Введите город, в который хотите поехать')
    bot.register_next_step_handler(message, check_city)
    command_list.append(message.text)


def check_city(message):
    bot.send_message(message.from_user.id, text='Выберите город', reply_markup=keyboard_city(message.text))
    bot.register_next_step_handler(message, check_in_date)


def check_in_date(message):
    command_list.append(message.text)
    calendar, step = DetailedTelegramCalendar().build()
    bot.send_message(message.from_user.id,
                     'Введите дату предполагаемого заселения',
                     reply_markup=calendar)

    @bot.callback_query_handler(func=DetailedTelegramCalendar.func())
    def cal(c):
        result, key, step = DetailedTelegramCalendar().process(c.data)
        if not result and key:
            bot.edit_message_text(f"Select {LSTEP[step]}",
                                  c.message.chat.id,
                                  c.message.message_id,
                                  reply_markup=key)
        elif result:
            bot.send_message(message.from_user.id, text=f"Вы выбрали дату заселения {result}. Напишите ок для "
                                                        f"продолжения?",
                             reply_markup=ReplyKeyboardRemove())
            command_list.append(result)

    bot.register_next_step_handler(message, check_out_date)


def check_out_date(message):
    calendar, step = DetailedTelegramCalendar().build()
    bot.send_message(message.from_user.id,
                     'Введите дату предполагаемого выселения',
                     reply_markup=calendar)

    @bot.callback_query_handler(func=DetailedTelegramCalendar.func())
    def cal(c):
        result, key, step = DetailedTelegramCalendar().process(c.data)
        if not result and key:
            bot.edit_message_text(f"Select {LSTEP[step]}",
                                  c.message.chat.id,
                                  c.message.message_id,
                                  reply_markup=key)
        elif result:
            bot.send_message(message.from_user.id, text=f"Вы выбрали дату выселения {result}. Напишите ок для "
                                                        f"продолжения?",
                             reply_markup=ReplyKeyboardRemove())
            command_list.append(result)

    bot.register_next_step_handler(message, hotels_count)


def hotels_count(message):
    bot.send_message(message.from_user.id, text='Сколько отелей Вы хотите посмотреть?', reply_markup=keyboard_number())
    bot.register_next_step_handler(message, is_photos)


def low(message):
    bot.send_message(message.from_user.id, 'Укажите самую дешевую цену, устраивающую вас',
                     reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(message, high)
    command_list.append(message.text)


def high(message):
    bot.send_message(message.from_user.id, 'Укажите самую дорогую цену, устраивающую вас')
    bot.register_next_step_handler(message, min)
    command_list.append(message.text)


def min(message):
    bot.send_message(message.from_user.id, 'Укажите минимально расстояние до центра, устраивающее вас')
    bot.register_next_step_handler(message, max)
    command_list.append(message.text)


def max(message):
    bot.send_message(message.from_user.id, 'Укажите максимальное расстояние до центра, устраивающее вас')
    bot.register_next_step_handler(message, is_photos)
    command_list.append(message.text)


def is_photos(message):
    bot.send_message(message.from_user.id, text='Хотите ли Вы посмотреть фотографии отелей?', reply_markup=keyboard_yesno())
    bot.register_next_step_handler(message, get_info)
    command_list.append(message.text)


def get_info(message):
    history_string = ''
    if message.text.lower() == 'нет':
        bot.send_message(message.from_user.id, 'Подождите немного, Ваш запрос обрабатывается',
                         reply_markup=ReplyKeyboardRemove())
        for i in get_bestdeal(city_id=find_destinationid(command_list[1]), low_price=int(command_list[5]),
                              high_price=int(command_list[6]),
                              min_distance=float(command_list[7]), max_distance=float(command_list[8]),
                              hotels_count=int(command_list[4]), checkin_date=command_list[2],
                              checkout_date=command_list[3], count_photo=0):
            bot.send_message(message.from_user.id, i)
            history_string += i
        us_id = message.from_user.id
        us_name = message.from_user.username
        update_history_db(us_id, us_name, history_string, command_list[0], datetime.datetime.now())
        command_list.clear()

    elif message.text.lower() == 'да':
        bot.send_message(message.from_user.id, text='Сколько фотографий Вы хотите посмотреть?', reply_markup=keyboard_number())
        bot.register_next_step_handler(message, get_info_with_photo)


def get_info_with_photo(message):
    history_string = ''
    command_list.append(message.text)
    bot.send_message(message.from_user.id, 'Подождите немного, Ваш запрос обрабатывается',
                     reply_markup=ReplyKeyboardRemove())
    for i in get_bestdeal(city_id=find_destinationid(command_list[1]), low_price=int(command_list[5]),
                              high_price=int(command_list[6]),
                              min_distance=float(command_list[7]), max_distance=float(command_list[8]),
                              hotels_count=int(command_list[4]), checkin_date=command_list[2],
                              checkout_date=command_list[3], count_photo=int(command_list[9])):
        bot.send_message(message.from_user.id, i)
        history_string += i
    us_id = message.from_user.id
    us_name = message.from_user.username
    update_history_db(us_id, us_name, history_string, command_list[0], datetime.datetime.now())
    command_list.clear()
