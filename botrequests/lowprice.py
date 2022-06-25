import json
import re
from pprint import pprint

import requests

from botrequests.common_requests import get_photo

from decouple import config

API_KEY = config('rapidapi-key')

headers = {
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com",
    "X-RapidAPI-Key": API_KEY
}


def get_lowprice(city, hotels_count, checkin_date, checkout_date, count_photo):
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    url_hotel = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = {"query": f'{city}'}

    hotels_list = []
    hotels_dict = {}
    distance_dict = {}
    response = requests.request("GET", url, headers=headers, params=querystring)
    found_city = response.json()
    for i in range(len(found_city["suggestions"])):
        for j in range((len(found_city["suggestions"][i]["entities"]))):
            if found_city["suggestions"][i]["entities"][j]["type"] == "CITY":
                city_id = found_city["suggestions"][i]["entities"][j]['destinationId']
                querystring_hotel = {"destinationId": city_id, "checkIn": checkin_date, "checkOut": checkout_date,
                                     "pageNumber": "1", "pageSize": hotels_count, "sortOrder": "PRICE"}

                response_hotel = requests.request("GET", url_hotel, headers=headers, params=querystring_hotel)
                found_hotels = json.loads(response_hotel.text)
                list_result = found_hotels['data']['body']['searchResults']['results']
                if not list_result:
                    return None, None
                for i_hotel in list_result:
                    distance = re.findall(r'\d[,.]?\d', i_hotel['landmarks'][0]['distance'])[0].replace(',', '.')
                    for count in range(hotels_count):
                        hotels_list.append(found_hotels['data']['body']['searchResults']['results'][count]['id'])
                        distance_dict[found_hotels['data']['body']['searchResults']['results'][count]['id']] = distance

                for count in range(hotels_count):
                    hotels_list.append(found_hotels['data']['body']['searchResults']['results'][count]['id'])


    url_detail = "https://hotels4.p.rapidapi.com/properties/get-details"
    for my_id in hotels_list:
        querystring_detail = {"id": my_id, "checkIn": checkin_date, "checkOut": checkout_date}

        response_hotels = requests.request("GET", url_detail, headers=headers, params=querystring_detail)
        hotels_info = response_hotels.json()
        hotels_dict[my_id] = "Название отеля:" + ' ' + hotels_info['data']['body']['propertyDescription']['name'] + '\n' + \
                                              'Адрес:' + ' ' + hotels_info['data']['body']['propertyDescription']['address'][
                                                  'addressLine1'] + '\n' + 'Расстояние до центра: ' + ' ' + distance_dict[my_id] + '\n' + 'Цена:' + ' ' + hotels_info['data']['body']['propertyDescription']['featuredPrice']['currentPrice']['formatted']
        if count_photo > 0:
            for ph in range(len(get_photo(count_photo, my_id))):
                hotels_dict[f'{my_id}'] += '\n' + get_photo(count_photo, my_id)[ph]

    return hotels_dict.values()


# # #
# pprint(get_lowprice('London, England, United Kingdom', 3, '2022-07-03', '2020-07-12', 0))
# print(select_lowprice_db())
