import json
import re
from pprint import pprint

import requests

from botrequests.common_requests import get_photo, headers


def get_bestdeal(city, low_price, high_price, min_distance, max_distance, hotels_count, photos_count, checkin_date,
                 checkout_date, page_number=1):
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    url_hotel = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = {"query": f'{city}'}
    response = requests.request("GET", url, headers=headers, params=querystring)
    found_city = response.json()
    hotels_list = []
    hotels_dict = {}
    distance_dict = {}

    while len(hotels_list) < hotels_count:
        for i in range(len(found_city["suggestions"])):
            for j in range((len(found_city["suggestions"][i]["entities"]))):
                if found_city["suggestions"][i]["entities"][j]["type"] == "CITY":
                    city_id = found_city["suggestions"][i]["entities"][j]['destinationId']
                    querystring_hotel = {"destinationId": city_id, "checkIn": checkin_date, "checkOut": checkout_date,
                                             "priceMin": low_price, "priceMax": high_price, "pageNumber": str(page_number), "sortOrder": "DISTANCE_FROM_LANDMARK"}

                    response_hotel = requests.request("GET", url_hotel, headers=headers, params=querystring_hotel)
                    data = json.loads(response_hotel.text)
                    list_result = data['data']['body']['searchResults']['results']
                    if not list_result:
                        return None, None
                    for i_hotel in list_result:
                        distance = re.findall(r'\d[,.]?\d', i_hotel['landmarks'][0]['distance'])[0].replace(',', '.')
                        if float(distance) <= max_distance and float(distance) >= min_distance:
                            for count in range(hotels_count):
                                hotels_list.append(data['data']['body']['searchResults']['results'][count]['id'])
                                distance_dict[data['data']['body']['searchResults']['results'][count]['id']] = distance
        page_number += 1
    url_detail = "https://hotels4.p.rapidapi.com/properties/get-details"
    for my_id in hotels_list[:hotels_count]:

        querystring_detail = {"id": my_id, "checkIn": checkin_date, "checkOut": checkout_date}

        response_detail = requests.request("GET", url_detail, headers=headers, params=querystring_detail)
        hotels_info = response_detail.json()
        try:
            if low_price <= float(hotels_info['data']['body']['propertyDescription']['featuredPrice']['currentPrice'][
                                          'plain']) <= high_price:

                hotels_dict[my_id] = "Название отеля:" + ' ' + hotels_info['data']['body']['propertyDescription']['name'] + '\n' + \
                                              'Адрес:' + ' ' + hotels_info['data']['body']['propertyDescription']['address'][
                                                  'addressLine1'] + '\n' + 'Расстояние до центра: ' + ' ' + distance_dict[my_id] + '\n' + 'Цена:' + ' ' + hotels_info['data']['body']['propertyDescription']['featuredPrice']['currentPrice']['formatted']
        except KeyError:
            hotels_dict[my_id] = hotels_info['data']['body']['propertyDescription']['name'] + '\n' + \
                                      hotels_info['data']['body']['propertyDescription']['address'][
                                          'addressLine1'] + '\nЦена по отелю недоступна'
            if photos_count > 0:
                for ph in range(len(get_photo(photos_count, my_id))):
                    hotels_dict[f'{my_id}'] += '\n' + get_photo(photos_count, my_id)[ph]

    return hotels_dict.values()
#
# print(get_bestdeal('London, England, United Kingdom', 20, 500, 0.2, 4, 3, 6, '2022-07-03', '2020-07-12'))
