
from pprint import pprint


import requests
from decouple import config

from botrequests.common_requests import get_photo

API_KEY = config('rapidapi-key')

headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


def get_lowprice(city, hotels_count, checkin_date, checkout_date, count_photo):
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    url_hotel = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = {"query": f'{city}'}

    hotels_list = []
    hotels_dict = {}
    response = requests.request("GET", url, headers=headers, params=querystring)
    found_city = response.json()
    for i in range(len(found_city["suggestions"])):
        for j in range((len(found_city["suggestions"][i]["entities"]))):
            if found_city["suggestions"][i]["entities"][j]["type"] == "CITY":
                city_id = found_city["suggestions"][i]["entities"][j]['destinationId']
                querystring_hotel = {"destinationId": city_id, "checkIn": checkin_date, "checkOut": checkout_date,
                                 "pageNumber": "1", "pageSize": hotels_count, "sortOrder": "PRICE"}

                response = requests.request("GET", url_hotel, headers=headers, params=querystring_hotel)
                found_hotels = response.json()
                for count in range(hotels_count):
                    hotels_list.append(found_hotels['data']['body']['searchResults']['results'][count]['id'])

    url_detail = "https://hotels4.p.rapidapi.com/properties/get-details"
    for my_id in hotels_list:
        querystring_detail = {"id": my_id, "checkIn": checkin_date, "checkOut": checkout_date}

        response_hotels = requests.request("GET", url_detail, headers=headers, params=querystring_detail)
        hotels_info = response_hotels.json()
        try:
            hotels_dict[f'{my_id}name'] = hotels_info['data']['body']['propertyDescription']['name']
            hotels_dict[f'{my_id}address'] = hotels_info['data']['body']['propertyDescription']['address'][
                'addressLine1']
            hotels_dict[f'{my_id}price'] = \
                hotels_info['data']['body']['propertyDescription']['featuredPrice']['currentPrice']['formatted']
            for ph in range(len(get_photo(count_photo, my_id))):
                hotels_dict[f'{my_id}photo{ph+1}'] = get_photo(count_photo, my_id)[ph]
        except KeyError:
            pass

    return hotels_dict.values()




#
# print(get_lowprice('Bern', 3, '2022-07-03', '2020-07-12', 0))
# print(select_lowprice_db())
