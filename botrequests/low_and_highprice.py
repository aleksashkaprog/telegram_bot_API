import json
import re

from botrequests.common_requests import headers, all_responses, get_photo


def find_hotels(**kwargs):
    hotels_list = []
    distance_dict = {}
    hotels_dict = {}
    url_hotel = "https://hotels4.p.rapidapi.com/properties/list"
    querystring_hotel = {"destinationId": kwargs['city_id'], "checkIn": kwargs['checkin_date'], "checkOut": kwargs['checkout_date'],
                         "pageNumber": "1", "pageSize": kwargs['hotels_count'], "sortOrder": kwargs['sortOrder']}
    found_hotels = json.loads(all_responses(url_hotel, headers, querystring_hotel).text)
    list_result = found_hotels['data']['body']['searchResults']['results']
    if not list_result:
        return None, None
    for i_hotel in list_result:
        distance = re.findall(r'\d[,.]?\d', i_hotel['landmarks'][0]['distance'])[0].replace(',', '.')
        for count in range(kwargs['hotels_count']):
            hotels_list.append(found_hotels['data']['body']['searchResults']['results'][count]['id'])
            distance_dict[found_hotels['data']['body']['searchResults']['results'][count]['id']] = distance

        for count in range(kwargs['hotels_count']):
            hotels_list.append(found_hotels['data']['body']['searchResults']['results'][count]['id'])

    url_detail = "https://hotels4.p.rapidapi.com/properties/get-details"
    for my_id in hotels_list:
        querystring_detail = {"id": my_id, "checkIn": kwargs['checkin_date'], "checkOut": kwargs['checkout_date']}

        hotels_info = all_responses(url_detail, headers, querystring_detail).json()
        hotels_dict[my_id] = "Название отеля:" + ' ' + hotels_info['data']['body']['propertyDescription'][
            'name'] + '\n' + \
                             'Адрес:' + ' ' + hotels_info['data']['body']['propertyDescription']['address'][
                                 'addressLine1'] + '\n' + 'Расстояние до центра: ' + ' ' + distance_dict[
                                 my_id] + '\n' + 'Цена:' + ' ' + \
                             hotels_info['data']['body']['propertyDescription']['featuredPrice']['currentPrice'][
                                 'formatted']
        if kwargs['count_photo'] > 0:
            for ph in range(len(get_photo(kwargs['count_photo'], my_id))):
                hotels_dict[my_id] += '\n' + get_photo(kwargs['count_photo'], my_id)[ph]

    return hotels_dict.values()

# print(find_hotels(city_id=332483, hotels_count=3, checkin_date='2022-07-03', checkout_date='2022-07-12', sortOrder="PRICE", count_photo=3))