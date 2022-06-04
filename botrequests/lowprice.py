from pprint import pprint

import requests
from decouple import config

API_KEY = config('rapidapi-key')


def get_lowprice(city, hotels_count):
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"

    querystring = {"query": f'{city}'}

    headers = {
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com",
        "X-RapidAPI-Key": API_KEY
    }

    lowprice_list_id = []
    lowprice_list_name = []
    hotels_list = []
    response = requests.request("GET", url, headers=headers, params=querystring)
    found_city = response.json()
    for i in range(len(found_city["suggestions"])):
        for j in range((len(found_city["suggestions"][i]["entities"]))):
            if found_city["suggestions"][i]["entities"][j]["type"] == "HOTEL":
                lowprice_list_id.append(found_city["suggestions"][i]["entities"][j]['destinationId'])
                lowprice_list_name.append(found_city["suggestions"][i]["entities"][j]['name'])

    for i in lowprice_list_id:
        url_hotel = "https://hotels4.p.rapidapi.com/properties/list"

        querystring_hotel = {"destinationId": f'{i}', "sortOrder": "PRICE"}

        response_hotel = requests.request("GET"[:hotels_count], url_hotel, headers=headers, params=querystring_hotel)

        found_hotel = response_hotel.json()

        hotels_list.append(found_hotel)
    return hotels_list


pprint(get_lowprice('New York', 1))
