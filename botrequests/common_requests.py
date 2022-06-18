from pprint import pprint

import requests
from decouple import config

API_KEY = config('rapidapi-key')

headers = {
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com",
    "X-RapidAPI-Key": API_KEY
}


def find_city(city):
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring = {"query": f'{city}'}

    hotels_list = []
    response = requests.request("GET", url, headers=headers, params=querystring)
    found_city = response.json()
    for i in range(len(found_city["suggestions"])):
        for j in range((len(found_city["suggestions"][i]["entities"]))):
            if found_city["suggestions"][i]["entities"][j]["type"] == "CITY":
                hotels_list.append(found_city["suggestions"][i]["entities"][j]['name'])
    return hotels_list


def get_photo(photos_count, hotel_id):
    import requests

    url_photo = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring_photo = {"id": hotel_id}
    photos_list = []
    response = requests.request("GET", url_photo, headers=headers, params=querystring_photo)
    hotel_photos = response.json()
    for i in range(photos_count):
        photos_list.append(hotel_photos['hotelImages'][i]['baseUrl'])
    return photos_list

# pprint(find_city('Bern'))
