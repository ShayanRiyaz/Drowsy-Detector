import googlemaps
import pprint
from urllib.parse import urlencode
import requests

API_KEY = 'AIzaSyBSDl8S2NWX5GwJHvLaQ2PMVJSSxur033Q'

gmaps = googlemaps.Client(key=API_KEY)

#Radius is in meters, curr lat+lon is ssrt to FIU, and only checks for open locations and gas stations
places_result = gmaps.places_nearby(location='25.751496994, -80.37333184', radius = 4000, open_now = True, type = 'gas_station')

#pprint.pprint(places_result)

for place in places_result['results']:
    place_id = place['place_id']
    fields = ['name', 'formatted_phone_number', 'geometry/location', 'opening_hours']
    place_details = gmaps.place(place_id = place_id, fields = fields)

    print(place_details)

start_lang = 37.3828025
start_long = -122.0791124
end_lang = 37.7862756
end_long = -122.4749331

def get_route_lat_long(API_KEY, start_lang, start_long,
                       end_lang, end_long,
                       data_type='json'):

    endpoint = f"https://maps.googleapis.com/maps/api/directions/{data_type}"
    params = {'origin': f'{start_lang},{start_long}',
              'key': API_KEY,
              'destination': f'{end_lang}, {end_long}',
              'mode': 'driving',
              'sensor': 'false'}
    url_params = urlencode(params)

    url = f"{endpoint}?{url_params}"

    r = requests.get(url)
    if r.status_code not in range(200,299):
        return {}
    return r.json()


def get_time_and_distance(route_json):
    distance_and_time = [0] * len(route_json['routes'][0]['legs'][0]['steps'])
    for i in range(len(route_json['routes'][0]['legs'][0]['steps'])):
        distance_and_time[i] = (route_json['routes'][0]['legs'][0]['steps'][i]['distance']['text'],route_json['routes'][0]['legs'][0]['steps'][i]['duration']['text'])
    return distance_and_time


def get_lat_long_from_route(route_json):
    journey_coords = [0] * len(route_json['routes'][0]['legs'][0]['steps'])
    for i in range(len(route_json['routes'][0]['legs'][0]['steps'])):
        journey_coords[i] = (route_json['routes'][0]['legs'][0]['steps'][i]['end_location']['lat'],route_json['routes'][0]['legs'][0]['steps'][i]['end_location']['lng'])
    
    return journey_coords


route_json = get_route_lat_long(API_KEY, start_lang, start_long,
                   end_lang, end_long)
#print(route_json)
distance_and_time = get_time_and_distance(route_json)
print(distance_and_time)
journey_coords = get_lat_long_from_route(route_json)
print(journey_coords)

# https://maps.googleapis.com/maps/api/directions/json?origin=37.3828025,-122.0791124&key=AIzaSyBSDl8S2NWX5GwJHvLaQ2PMVJSSxur033Q&destination=37.7862756, -122.4749331&mode=driving&sensor=false
