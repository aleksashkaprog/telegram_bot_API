import json
import re

from botrequests.common_requests import all_responses, get_photo, headers


def get_bestdeal(**kwargs):
    url_hotel = "https://hotels4.p.rapidapi.com/properties/list"
    hotels_list = []
    distance_dict = {}
    hotels_dict = {}

    while len(hotels_list) < kwargs['hotels_count']:
        querystring_hotel = {
            "destinationId": kwargs['city_id'],
            "checkIn": kwargs['checkin_date'],
            "checkOut": kwargs['checkout_date'],
            "priceMin": kwargs['low_price'],
            "priceMax": kwargs['high_price'],
            "pageNumber": str(kwargs['page_number']),
            "sortOrder": "DISTANCE_FROM_LANDMARK",
        }

        data = json.loads(all_responses(url_hotel, headers, querystring_hotel).text)
        list_result = data['data']['body']['searchResults']['results']
        if not list_result:
            return None, None
        for i_hotel in list_result:
            distance = re.findall(r'\d[,.]?\d', i_hotel['landmarks'][0]['distance'])[0].replace(',', '.')
            if kwargs['max_distance'] >= float(distance) >= kwargs['min_distance']:
                for count in range(kwargs['hotels_count']):
                    hotels_list.append(data['data']['body']['searchResults']['results'][count]['id'])
                    distance_dict[data['data']['body']['searchResults']['results'][count]['id']] = distance
        kwargs['page_number'] += 1

    url_detail = "https://hotels4.p.rapidapi.com/properties/get-details"
    for my_id in hotels_list[:kwargs['hotels_count']]:

        querystring_detail = {"id": my_id, "checkIn": kwargs['checkin_date'], "checkOut": kwargs['checkout_date']}
        hotels_info = all_responses(url_detail, headers, querystring_detail).json()
        try:
            if kwargs['low_price'] <= float(
                    hotels_info['data']['body']['propertyDescription']['featuredPrice']['currentPrice'][
                        'plain']) <= kwargs['high_price']:
                hotels_dict[my_id] = "Название отеля:" + ' ' + hotels_info['data']['body']['propertyDescription'][
                    'name'] + '\n' + \
                                     'Адрес:' + ' ' + hotels_info['data']['body']['propertyDescription']['address'][
                                         'addressLine1'] + '\n' + 'Расстояние до центра: ' + ' ' + distance_dict[
                                         my_id] + '\n' + 'Цена:' + ' ' + \
                                     hotels_info['data']['body']['propertyDescription']['featuredPrice'][
                                         'currentPrice']['formatted']
            if kwargs['count_photo'] > 0:
                for ph in range(len(get_photo(kwargs['count_photo'], my_id))):
                    hotels_dict[my_id] += '\n' + get_photo(kwargs['count_photo'], my_id)[ph]
        except KeyError:
            hotels_dict[my_id] = hotels_info['data']['body']['propertyDescription']['name'] + '\n' + \
                                 hotels_info['data']['body']['propertyDescription']['address'][
                                     'addressLine1'] + '\nЦена по отелю недоступна'
    return hotels_dict.values()
