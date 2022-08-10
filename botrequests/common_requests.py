import json
import re
from pprint import pprint

import requests
from decouple import config

from config_data.config import RAPID_API_KEY

headers = {
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com",
    "X-RapidAPI-Key": RAPID_API_KEY
}


def all_responses(my_url, my_headers, my_params):
    response = requests.request("GET", my_url, headers=my_headers, params=my_params, timeout=15)
    try:
        if response.status_code == 200:
            return response
    except requests.exceptions.ReadTimeout:
        return print('Ошибка на сервере, время ожидания ответа сервера истекло. Пожалуйста, попробуйте повторить Ваш '
                     'запрос')
        pass


def find_city(city):
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring = {"query": f'{city}'}
    my_city = re.sub(r'<span.*?>', '', all_responses(url, headers, querystring).text).replace('</span>', '')
    city_list = []
    found_city = json.loads(my_city)
    for i in found_city["suggestions"]:
        for j in i["entities"]:
            if j["type"] == "CITY":
                city_list.append(j['caption'])

    return city_list


def find_destinationid(city_name):
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring = {"query": f'{city_name}'}
    found_city = all_responses(url, headers, querystring).json()
    for i in found_city["suggestions"]:
        for j in i["entities"]:
            if j["type"] == "CITY":
                city_id = j['destinationId']
                return city_id


def get_photo(photos_count, hotel_id):
    url_photo = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring_photo = {"id": hotel_id}
    photos_list = []
    hotel_photos = all_responses(url_photo, headers, querystring_photo).json()
    for i in range(photos_count):
        photos_list.append(hotel_photos['hotelImages'][i]['baseUrl'].format(size='z'))
    return photos_list

# print(get_photo(5, 532733))
# print(find_city('London'))