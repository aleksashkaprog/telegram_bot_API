from telebot import types

from botrequests.common_requests import find_city


def keyboard_city(city):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in find_city(city):
        btn = types.KeyboardButton(text=str(i))
        markup.add(btn)
    return markup


def keyboard_yesno():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Да')
    btn2 = types.KeyboardButton('Нет')
    markup.add(btn1, btn2)
    return markup


def keyboard_number():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(1, 11):
        btn = types.KeyboardButton(text=str(i))
        markup.add(btn)
    return markup
