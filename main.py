# coding: utf-8
import datetime
import os

import telebot
from decouple import config

from telebot import types
from telebot.types import CallbackQuery, ReplyKeyboardRemove
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE


from botrequests.bestdeal import get_bestdeal
from botrequests.common_requests import find_city
from botrequests.hightprice import get_highprice
from botrequests.history import update_history_db, get_history_db
from botrequests.lowprice import get_lowprice

calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_1_callback = CallbackData("calendar_1", "action", "year", "month", "day")

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
        command_list.append(message.text)



    elif message.text == '/history':
        for his in get_history_db(message.from_user.username):
            bot.send_message(message.from_user.id, his)

    else:
        bot.send_message(message.from_user.id, 'Я не понимаю эту команду, '
                                               'напишите "/help" для просмотра доступных команд')

    if message.text != '/lowprice' or message.text != '/highprice' or message.text != '/bestdeal':
        us_id = message.from_user.id
        us_name = message.from_user.username
        update_history_db(us_id, us_name, 'no', message.text, datetime.datetime.now())


def check_city(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in find_city(message.text):
        btn = types.KeyboardButton(text=str(i))
        markup.add(btn)
    bot.send_message(message.from_user.id, text='Выберите город', reply_markup=markup)
    bot.register_next_step_handler(message, check_in_date)


def check_in_date(message):
    bot.send_message(message.from_user.id, 'Введите дату предполагаемого заселения')
    bot.register_next_step_handler(message, check_out_date)
    command_list.append(message.text)






def check_out_date(message):
    bot.send_message(message.from_user.id, 'Введите дату предполагаемого выселения')
    bot.register_next_step_handler(message, hotels_count)
    command_list.append(message.text)


def hotels_count(message):
    markup = types.ReplyKeyboardMarkup()
    for i in range(1, 11):
        btn = types.KeyboardButton(text=str(i))
        markup.add(btn)
    bot.send_message(message.from_user.id, text='Сколько отелей Вы хотите посмотреть?', reply_markup=markup)
    if command_list[0] == '/bestdeal':
        bot.register_next_step_handler(message, low)
    else:
        bot.register_next_step_handler(message, is_photos)
    command_list.append(message.text)


def is_photos(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Да')
    btn2 = types.KeyboardButton('Нет')
    markup.add(btn1, btn2)
    bot.send_message(message.from_user.id, text='Хотите ли Вы посмотреть фотографии отелей?', reply_markup=markup)
    bot.register_next_step_handler(message, get_info)
    command_list.append(message.text)


def get_info(message):
    history_string = ''
    bot.send_message(message.from_user.id, 'Подождите немного, Ваш запрос обрабатывается')
    if message.text.lower() == 'нет':
        if command_list[0] == '/lowprice':
            for i in get_lowprice(city=command_list[1], hotels_count=int(command_list[4]), checkin_date=command_list[2],
                                  checkout_date=command_list[3], count_photo=0):
                bot.send_message(message.from_user.id, i)
                history_string += i

        elif command_list[0] == '/highprice':
            for i in get_highprice(city=command_list[1], hotels_count=int(command_list[4]),
                                   checkin_date=command_list[2],
                                   checkout_date=command_list[3], count_photo=0):
                bot.send_message(message.from_user.id, i)
                history_string += i
        elif command_list[0] == '/bestdeal':
            for i in get_bestdeal(city=command_list[1], low_price=int(command_list[5]), high_price=int(command_list[6]),
                                  min_distance=float(command_list[7]), max_distance=float(command_list[8]),
                                  hotels_count=int(command_list[4]), photos_count=0, checkin_date=command_list[2],
                                  checkout_date=command_list[3]):
                bot.send_message(message.from_user.id, i)
                history_string += i
        us_id = message.from_user.id
        us_name = message.from_user.username
        update_history_db(us_id, us_name, history_string, command_list[0], datetime.datetime.now())
        command_list.clear()

    elif message.text.lower() == 'да':
        markup = types.ReplyKeyboardMarkup()
        for i in range(1, 11):
            btn = types.KeyboardButton(text=str(i))
            markup.add(btn)
        bot.send_message(message.from_user.id, text='Сколько фотографий Вы хотите посмотреть?', reply_markup=markup)
        bot.register_next_step_handler(message, get_info_with_photo)


def get_info_with_photo(message):
    history_string = ''
    command_list.append(message.text)
    bot.send_message(message.from_user.id, 'Подождите немного, Ваш запрос обрабатывается')
    if command_list[0] == '/lowprice':
        for i in get_lowprice(city=command_list[1], hotels_count=int(command_list[4]), checkin_date=command_list[2],
                              checkout_date=command_list[3], count_photo=int(command_list[5])):
            bot.send_message(message.from_user.id, i)
            history_string += i
    elif command_list[0] == '/highprice':
        for i in get_highprice(city=command_list[1], hotels_count=int(command_list[4]), checkin_date=command_list[2],
                               checkout_date=command_list[3], count_photo=int(command_list[5])):
            bot.send_message(message.from_user.id, i)
            history_string += i
    elif command_list[0] == '/bestdeal':
        for i in get_bestdeal(city=command_list[1], low_price=int(command_list[5]), high_price=int(command_list[6]),
                                  min_distance=float(command_list[7]), max_distance=float(command_list[8]),
                                  hotels_count=int(command_list[4]), photos_count=int(command_list[9]), checkin_date=command_list[2],
                                  checkout_date=command_list[3]):
            bot.send_message(message.from_user.id, i)
            us_id = message.from_user.id
            us_name = message.from_user.username
            update_history_db(us_id, us_name, history_string, command_list[0], datetime.datetime.now())
    command_list.clear()


def low(message):
    bot.send_message(message.from_user.id, 'Укажите самую дешевую цену, устраивающую вас')
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


@bot.message_handler(commands='datetime')
def check_other_messages(message):
    """
    Catches a message with the command "start" and sends the calendar
    :param message:
    :return:
    """

    now = datetime.datetime.now()  # Get the current date
    bot.send_message(
        message.chat.id,
        "Selected date",
        reply_markup=calendar.create_calendar(
            name=calendar_1_callback.prefix,
            year=now.year,
            month=now.month,  # Specify the NAME of your calendar
        ),
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(calendar_1_callback.prefix)
)
def callback_inline(call: CallbackQuery):
    """
    Обработка inline callback запросов
    :param call:
    :return:
    """

    # At this point, we are sure that this calendar is ours. So we cut the line by the separator of our calendar
    name, action, year, month, day = call.data.split(calendar_1_callback.sep)
    # Processing the calendar. Get either the date or None if the buttons are of a different type
    date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    # There are additional steps. Let's say if the date DAY is selected, you can execute your code. I sent a message.
    if action == "DAY":
        bot.send_message(
            chat_id=call.from_user.id,
            text=f"You have chosen {date.strftime('%d.%m.%Y')}",
            reply_markup=ReplyKeyboardRemove(),
        )
        print(f"{calendar_1_callback}: Day: {date.strftime('%d.%m.%Y')}")
    elif action == "CANCEL":
        bot.send_message(
            chat_id=call.from_user.id,
            text="Cancellation",
            reply_markup=ReplyKeyboardRemove(),
        )
        print(f"{calendar_1_callback}: Cancellation")

bot.polling()
