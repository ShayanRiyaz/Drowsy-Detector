import googlemaps
import pprint
from urllib.parse import urlencode
import requests
from googlemaps.convert import decode_polyline, encode_polyline
import json
from datetime import datetime
import math
import numpy
from collections import OrderedDict
import sys

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
    # pprint.pprint(places)
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

def address_mapper(start_address, end_address):
    address = start_address
    start_lat,start_long = get_lat_long_from_address(address)
    #print(start_lat,start_long)
    #print(type(start_lat),type(start_long))

    end_address = end_address
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
    return journey_coords
    # simulate_coords_with_time(time_list,journey_coords)






def _calculate_distance(origin, destination):
    """
    Calculate the Haversine distance. 
    This isn't accurate for large distances, but for our purposes it is good enough
    """
    lat1, lon1 = origin['lat'], origin['lng']
    lat2, lon2 = destination['lat'], destination['lng']
    radius = 6371000  # metres

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d

def _round_up_time(time, period):
    """
    Rounds up time to the higher multiple of period
    For example, if period=5, then time=16s will be rounded to 20s
    if time=15, then time will remain 15
    """
    # If time is an exact multiple of period, don't round up
    if time % period == 0:
        return time

    time = round(time)
    return time + period - (time % period)

def _fill_missing_times(times, lats, lngs, period):
    start_time = times[0]
    end_time = times[-1]
    
    new_times = range(start_time, end_time + 1, period)
    new_lats = numpy.interp(new_times, times, lats).tolist()
    new_lngs = numpy.interp(new_times, times, lngs).tolist()

    return new_times, new_lats, new_lngs

def get_points_along_path(maps_api_key, _from, _to, departure_time=None, period=5):
    """
    Generates a series of points along the route, such that it would take approx `period` seconds to travel between consecutive points
    
    This function is primarily meant to simulate a car along a route. The output of this function is equivalent to the geo coordinates 
    of the car every 5 seconds (assuming period = 5)
    
    _from = human friendly from address that google maps can understand
    _to = human friendly to address that google maps can understand
    departure_time - primarily used to identify traffic model, defaults to current time
    period = how frequently should co-ordinates be tracked? Defaults to 5 seconds

    The output is an OrderedDict. Key is the time in seconds since trip start, value is a tuple representing (lat, long) in float

    >>> python vehicles.py "hashedin technologies, bangalore" "cubbon park"
    """
    if not departure_time:
        departure_time = datetime.now()

    gmaps = googlemaps.Client(key=maps_api_key)
    directions = gmaps.directions(_from, _to, departure_time=departure_time)
    
    steps = directions[0]['legs'][0]['steps']
    all_lats = []
    all_lngs = []
    all_times = []

    step_start_duration = 0
    step_end_duration = 0

    for step in steps:
        step_end_duration += step['duration']['value']
        points = decode_polyline(step['polyline']['points'])
        distances = []
        lats = []
        lngs = []
        start = None
        for point in points:
            if not start:
                start = point
                distance = 0
            else:
                distance = _calculate_distance(start, point)
            distances.append(distance)
            lats.append(point['lat'])
            lngs.append(point['lng'])
            
        missing_times = numpy.interp(distances[1:-1], [distances[0], distances[-1]], [step_start_duration, step_end_duration]).tolist()
        times = [step_start_duration] + missing_times + [step_end_duration]
        times = [_round_up_time(t, period) for t in times]
        
        times, lats, lngs = _fill_missing_times(times, lats, lngs, period)
        
        all_lats += lats
        all_lngs += lngs
        all_times += times

        step_start_duration = step_end_duration

    points = OrderedDict()
    for p in zip(all_times, all_lats,all_lngs):
        points[p[0]] = (round(p[1], 5), round(p[2],5))
        
    return points


def generate_polyline(points):
    return encode_polyline(points.values())    


def simulated_user_path(start_address, end_address):
    points = get_points_along_path(API_KEY,start_address,end_address)

    times,coords = [],[]
    for time,geo in points.items():
        times.append(times)
        coords.append(geo)
    
    return times,coords
