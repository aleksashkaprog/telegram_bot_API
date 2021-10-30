#coding: utf-8
import telebot


bot = telebot.TeleBot('2073523840:AAGkBX1cxLalJg8GBKzkQW_gYd4ct2tZTBk')


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