# coding: utf-8
import datetime
import os

import telebot
from decouple import config

from telebot import types

from botrequests.common_requests import find_city
from botrequests.hightprice import get_highprice
from botrequests.history import update_history_db, get_history_db, update_history_hotels_db
from botrequests.lowprice import get_lowprice

os.environ['token_tg'] = 'token'
TOKEN = os.getenv('token_tg')
bot = telebot.TeleBot(config(TOKEN))

command_list = []
history_list = []


@bot.message_handler(content_types=['text', 'content_types'])
def get_text_messages(message):
    if message.text.lower() == 'привет' or message.text == '/helloworld':
        bot.send_message(message.from_user.id, 'Здравствуйте! '
                                               'Вас приветствует телеграм-бот турагенства "Too Easy Travel". '
                                               'Чем я могу помочь Вам?'
                                               'Доступные команды:'
                                               '/lowprice - подборка самых дешевых отелей;'
                                               '/highprice - подборка самых дорогих отелей;'
                                               '/bestdeal - вывод отелей, наиболее подходящих по цене '
                                               'и расположению от центра')

    elif message.text == '/help':
        bot.send_message(message.from_user.id, 'Доступные команды:'
                                               '/lowprice - подборка самых дешевых отелей;'
                                               '/highprice - подборка самых дорогих отелей;'
                                               '/bestdeal - вывод отелей, наиболее подходящих по цене '
                                               'и расположению от центра')

    elif message.text == '/lowprice' or message.text == '/highprice' or message.text == '/bestdeal':
        bot.send_message(message.from_user.id, 'Введите город, в который хотите поехать')
        bot.register_next_step_handler(message, check_city)


    elif message.text == '/history':
        for his in get_history_db(message.from_user.username):
            bot.send_message(message.from_user.id, his)

    else:
        bot.send_message(message.from_user.id, 'Я не понимаю эту команду, '
                                               'напишите "/help" для просмотра доступных команд')
    us_id = message.from_user.id
    us_name = message.from_user.username
    update_history_db(us_id, us_name, message.text, datetime.datetime.now())


def check_city(message):
    for i in find_city(message.text):
        bot.send_message(message.from_user.id, i)
    bot.register_next_step_handler(message, check_in_date)
    command_list.append(message.text)


def check_in_date(message):
    bot.send_message(message.from_user.id, 'Введите дату предполагаемого заезда')
    bot.register_next_step_handler(message, check_out_date)
    command_list.append(message.text)


def check_out_date(message):
    bot.send_message(message.from_user.id, 'Введите дату предполагаемого выселения')
    bot.register_next_step_handler(message, hotels_count)
    command_list.append(message.text)


def hotels_count(message):
    bot.send_message(message.from_user.id, 'Сколько отелей Вы хотите посмотреть (не более 10)?')
    if command_list[0] == '/bestdeal':
        bot.register_next_step_handler(message, low)
    else:
        bot.register_next_step_handler(message, is_photos)
    command_list.append(message.text)


def is_photos(message):
    bot.send_message(message.from_user.id, 'Хотите ли Вы посмотреть фотографии отелей?')
    bot.register_next_step_handler(message, get_info)
    command_list.append(message.text)


def get_info(message):
    if message.text.lower() == 'нет':
        if command_list[0] == '/lowprice':
            for i in get_lowprice(city=command_list[1], hotels_count=int(command_list[2]), checkin_date=command_list[1],
                              checkout_date=command_list[3], count_photo=0):
                bot.send_message(message.from_user.id, i)
                update_history_hotels_db(i)
        elif command_list[0] == '/highrice':
            for i in get_highprice(city=command_list[1], hotels_count=int(command_list[2]), checkin_date=command_list[1],
                              checkout_date=command_list[3], count_photo=0):
                bot.send_message(message.from_user.id, i)
                update_history_hotels_db(i)
        command_list.clear()

    elif message.text.lower() == 'да':
        bot.send_message(message.from_user.id, 'Сколько фотографий Вы хотите посмотреть (не более 10)?')
        bot.register_next_step_handler(message, get_info_with_photo)


def get_info_with_photo(message):
    command_list.append(message.text)
    if command_list[0] == '/lowprice':
        for i in get_lowprice(city=command_list[1], hotels_count=int(command_list[2]), checkin_date=command_list[1],
                              checkout_date=command_list[3], count_photo=int(command_list[5])):
            bot.send_message(message.from_user.id, i)
            update_history_hotels_db(i)
    elif command_list[0] == '/highprice':
        for i in get_highprice(city=command_list[1], hotels_count=int(command_list[2]), checkin_date=command_list[1],
                          checkout_date=command_list[3], count_photo=int(command_list[5])):
            bot.send_message(message.from_user.id, i)
            update_history_hotels_db(i)
    command_list.clear()


def low(message):
    bot.send_message(message.from_user.id, 'Укажите самую дешевую цену, устраивающую вас')
    bot.register_next_step_handler(message, high)
    command_list.append(message.text)


def high(message):
    bot.send_message(message.from_user.id, 'Укажите самую дорогую цену, устраивающую вас')
    bot.register_next_step_handler(message, is_photos)
    command_list.append(message.text)


bot.polling()
