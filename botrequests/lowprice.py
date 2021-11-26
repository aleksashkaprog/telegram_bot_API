import main
from main import bot

@bot.message_handler(content_types=['text'])
def commands_bot(message):
    if message.text == '/lowprice':
        city = input('Введите город, куда хотите поехать: ')
        hotels_count = int(input('Какое количество отелей вы хотите посмотреть? (от 1 до 10)'))
        main.bot.send_message(message.from_user.id, main.querystring)