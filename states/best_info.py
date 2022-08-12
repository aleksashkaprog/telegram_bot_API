from telebot.handler_backends import State, StatesGroup


class BestInfoState(StatesGroup):
    city_id = State()
    hotels_count = State()
    checkin_date = State()
    checkout_date = State()
    count_photo = State()
    low_price = State()
    high_price = State()
    min_distance = State()
    max_distance = State()
