from telebot.handler_backends import State, StatesGroup


class HotelInfoState(StatesGroup):
    city_id = State()
    hotels_count = State()
    checkin_date = State()
    checkout_date = State()
    count_photo = State()
