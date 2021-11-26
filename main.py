#coding: utf-8
import os
import telebot
import requests
from decouple import config

url = "https://hotels4.p.rapidapi.com/locations/search"
querystring = {"query": "new york", "locale": "en_US"}
headers = {
    'x-rapidapi-host': "hotels4.p.rapidapi.com",
    'x-rapidapi-key': "00bce2701emsh37560fcb97ec654p1ec40ejsn4f564a3f117b"
    }
response = requests.request("GET", url, headers=headers, params=querystring)

os.environ['token_tg'] = 'token'
TOKEN = os.getenv('token_tg')
bot = telebot.TeleBot(config(TOKEN))


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == 'Привет'.lower() or message.text == '/helloworld':
        bot.send_message(message.from_user.id, 'Здравствуйте! '
                                               'Вас приветствует телеграм-бот турагенства "Too Easy Travel". '
                                               'Чем я могу помочь Вам?')
    elif message.text == '/help':
        bot.send_message(message.from_user.id, 'Напишите Привет:)')

    else:
        bot.send_message(message.from_user.id, 'Я не понимаю, используйте команду /help')





bot.polling()