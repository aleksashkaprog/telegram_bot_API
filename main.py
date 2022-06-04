#coding: utf-8
import os
import telebot
from decouple import config

os.environ['token_tg'] = 'token'
TOKEN = os.getenv('token_tg')
bot = telebot.TeleBot(config(TOKEN))


@bot.message_handler(content_types=['text'])
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

    elif message.text == '/lowprice' or message.text == '/highprice':
        bot.send_message(message.from_user.id, 'Введите город, в который хотите поехать')
        bot.register_next_step_handler(message, check_in_date)

    elif message.text == '/bestdeal':
        bot.send_message(message.from_user.id, 'Введите город, в который хотите поехать')
        bot.register_next_step_handler(message, low)

    else:
        bot.send_message(message.from_user.id, 'Я не понимаю эту команду, '
                                               'напишите "/help" для просмотра доступных команд')


def check_in_date(message):
    bot.send_message(message.from_user.id, 'Введите дату предполагаемого заезда')
    bot.register_next_step_handler(message, check_out_date)


def check_out_date(message):
    bot.send_message(message.from_user.id, 'Введите дату предполагаемого выселения')
    bot.register_next_step_handler(message, hotels_count)

def hotels_count(message):
    bot.send_message(message.from_user.id, 'Сколько отелей Вы хотите посмотреть (не более 10)?')
    bot.register_next_step_handler(message, is_photos)


def is_photos(message):
    bot.send_message(message.from_user.id, 'Хотите ли Вы посмотреть фотографии отелей?')
    if message.text.lower() == 'да':
        bot.register_next_step_handler(message, get_photos)
    # else:
    #     bot.send_message(message.from_user.id, get_lowprice())


def get_photos(message):
    bot.send_message(message.from_user.id, 'Сколько фотографий Вы хотите посмотреть (не более 10)?')
    # bot.send_message(message.from_user.id, get_lowprice())


def low(message):
    bot.send_message(message.from_user.id, 'Укажите самую дешевую цену, устраивающую вас')
    bot.register_next_step_handler(message, high)

def high(message):
    bot.send_message(message.from_user.id, 'Укажите самую дорогую цену, устраивающую вас')
    bot.register_next_step_handler(message, hotels_count)


bot.polling()