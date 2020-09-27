import googlemaps
import pprint
from urllib.parse import urlencode
import requests

API_KEY = 'AIzaSyBSDl8S2NWX5GwJHvLaQ2PMVJSSxur033Q'

gmaps = googlemaps.Client(key=API_KEY)

def get_lat_long_from_address(address,data_type = 'json'): 
    endpoint = f"https://maps.googleapis.com/maps/api/geocode/{data_type}"
    params = {'address': address,
                'key' : API_KEY}
    url_params = urlencode(params)
    url = f'{endpoint}?{url_params}'
    r = requests.get(url)
    if r.status_code not in range(200,299):
        return {}
    latlng = {}
    try:
        latlng = r.json()['results'][0]['geometry']['location']
    except:
        pass
    return float(latlng.get('lat')),float(latlng.get('lng'))

def get_route_lat_long(API_KEY, start_lat, start_long,
                       end_lat, end_long,
                       data_type='json'):

    endpoint = f"https://maps.googleapis.com/maps/api/directions/{data_type}"
    params = {'origin': f'{start_lat},{start_long}',
              'key': API_KEY,
              'destination': f'{end_lat}, {end_long}',
              'mode': 'driving',
              'sensor': 'false'}
    url_params = urlencode(params)

    url = f"{endpoint}?{url_params}"

    r = requests.get(url)
    if r.status_code not in range(200,299):
        return {}
    return r.json()


def get_time_and_distance(route_json,distance = True):
    
    if not distance:
        time_list = [0] * len(route_json['routes'][0]['legs'][0]['steps'])
        for i in range(len(route_json['routes'][0]['legs'][0]['steps'])):
            time_list[i] = (route_json['routes'][0]['legs'][0]['steps'][i]['duration']['value'])
        return time_list
    else:
        distance_and_time = [0] * len(route_json['routes'][0]['legs'][0]['steps'])
        for i in range(len(route_json['routes'][0]['legs'][0]['steps'])):
            distance_and_time[i] = (route_json['routes'][0]['legs'][0]['steps'][i]['distance']['value'],route_json['routes'][0]['legs'][0]['steps'][i]['duration']['value'])
        return distance_and_time


def get_lat_long_from_route(route_json):
    journey_coords = [0] * len(route_json['routes'][0]['legs'][0]['steps'])
    for i in range(len(route_json['routes'][0]['legs'][0]['steps'])):
        journey_coords[i] = (route_json['routes'][0]['legs'][0]['steps'][i]['end_location']['lat'],route_json['routes'][0]['legs'][0]['steps'][i]['end_location']['lng'])
    
    return journey_coords

def find_places(journey_coords_1,journey_coords_2):
    # Radius is in meters, curr lat+lon is ssrt to FIU, and only checks for open locations and gas stations
    places_result = gmaps.places_nearby(location=f'{journey_coords_1}, {journey_coords_2}', radius=4000, open_now=True,
                                        type='gas_station')

    # directions = gmaps.directions(origin= '9980 SW 104th St, Miami, FL 33176', destination = '1375 E Buena Vista
    # Dr, Orlando, FL 32830', mode = "driving")

    # This gets the places near the Current location
    places = gmaps.places(query="Rest Stops", location='25.751496994, -80.37333184', radius=4000, open_now=True)
    #pprint.pprint(places)
    for place in places['results']:
        place_id = place['place_id']
        fields = ['name', 'formatted_phone_number', 'geometry/location']
        place_details = gmaps.place(place_id=place_id, fields=fields)
        print(place_details)

    print('\n\n\n\n\n')

    for place in places_result['results']:
        place_id = place['place_id']
        fields = ['name', 'formatted_phone_number', 'geometry/location']
        place_details = gmaps.place(place_id=place_id, fields=fields)
        print(place_details)


# def simulate_coords_with_time(time_list,journey_coords):
#     for i in range(len(journey_coords)):
#         print(f'Currently at {journey_coords[i]}')
#         print(f'Travelling to next stop : ETA {time_list[i]} seconds')
#         time.sleep(time_list[i]/100)
#         # Get  ```find_places``` to work here

#     return 'Done'

address = '706 Rowell Avenue,Long Beach, CA'
start_lat,start_long = get_lat_long_from_address(address)
#print(start_lat,start_long)
#print(type(start_lat),type(start_long))

end_address = 'San Francisco, CA'
end_lat,end_long = get_lat_long_from_address(end_address)
#print(end_lat,end_long)
#print(type(end_lat),type(end_long))

route_json = get_route_lat_long(API_KEY, start_lat, start_long,
                   end_lat, end_long)

#print(route_json)
time_list = get_time_and_distance(route_json,distance = False)
print(f'(Time)\n{time_list}')
journey_coords = get_lat_long_from_route(route_json)
print(f'(Latitude, Longitude)\n{journey_coords}')
#simulate_coords_with_time(time_list,journey_coords) 
