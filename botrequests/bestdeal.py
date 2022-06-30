import json
import re
from pprint import pprint

import requests

from botrequests.common_requests import get_photo, headers, all_responses


def get_bestdeal(city_id, low_price, high_price, min_distance, max_distance, hotels_count, checkin_date,
                 checkout_date, count_photo, page_number=1):
    url_hotel = "https://hotels4.p.rapidapi.com/properties/list"
    hotels_list = []
    distance_dict = {}
    hotels_dict = {}

    while len(hotels_list) < hotels_count:
        querystring_hotel = {"destinationId": city_id, "checkIn": checkin_date, "checkOut": checkout_date,
                             "priceMin": low_price, "priceMax": high_price, "pageNumber": str(page_number),
                             "sortOrder": "DISTANCE_FROM_LANDMARK"}

        data = json.loads(all_responses(url_hotel, headers, querystring_hotel).text)
        list_result = data['data']['body']['searchResults']['results']
        if not list_result:
            return None, None
        for i_hotel in list_result:
            distance = re.findall(r'\d[,.]?\d', i_hotel['landmarks'][0]['distance'])[0].replace(',', '.')
            if max_distance >= float(distance) >= min_distance:
                for count in range(hotels_count):
                    hotels_list.append(data['data']['body']['searchResults']['results'][count]['id'])
                    distance_dict[data['data']['body']['searchResults']['results'][count]['id']] = distance
        page_number += 1

    url_detail = "https://hotels4.p.rapidapi.com/properties/get-details"
    for my_id in hotels_list[:hotels_count]:

        querystring_detail = {"id": my_id, "checkIn": checkin_date, "checkOut": checkout_date}
        hotels_info = all_responses(url_detail, headers, querystring_detail).json()
        try:
            if low_price <= float(hotels_info['data']['body']['propertyDescription']['featuredPrice']['currentPrice'][
                                      'plain']) <= high_price:
                hotels_dict[my_id] = "Название отеля:" + ' ' + hotels_info['data']['body']['propertyDescription'][
                    'name'] + '\n' + \
                                     'Адрес:' + ' ' + hotels_info['data']['body']['propertyDescription']['address'][
                                         'addressLine1'] + '\n' + 'Расстояние до центра: ' + ' ' + distance_dict[
                                         my_id] + '\n' + 'Цена:' + ' ' + \
                                     hotels_info['data']['body']['propertyDescription']['featuredPrice'][
                                         'currentPrice']['formatted']
            if count_photo > 0:
                for ph in range(len(get_photo(count_photo, my_id))):
                    hotels_dict[my_id] += '\n' + get_photo(count_photo, my_id)[ph]
        except KeyError:
            hotels_dict[my_id] = hotels_info['data']['body']['propertyDescription']['name'] + '\n' + \
                                 hotels_info['data']['body']['propertyDescription']['address'][
                                     'addressLine1'] + '\nЦена по отелю недоступна'
    return hotels_dict.values()
#
# print(get_bestdeal('London, England, United Kingdom', 20, 500, 0.2, 4, 3, 6, '2022-07-03', '2020-07-12'))
