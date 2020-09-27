import googlemaps
from googlemaps.convert import decode_polyline, encode_polyline
import json
from datetime import datetime
import math
import numpy
from collections import OrderedDict
import sys


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

        missing_times = numpy.interp(distances[1:-1], [distances[0], distances[-1]],
                                     [step_start_duration, step_end_duration]).tolist()
        times = [step_start_duration] + missing_times + [step_end_duration]
        times = [_round_up_time(t, period) for t in times]

        times, lats, lngs = _fill_missing_times(times, lats, lngs, period)

        all_lats += lats
        all_lngs += lngs
        all_times += times

        step_start_duration = step_end_duration

    points = OrderedDict()
    for p in zip(all_times, all_lats, all_lngs):
        points[p[0]] = (round(p[1], 5), round(p[2], 5))

    return points


def generate_polyline(points):
    return encode_polyline(points.values())


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python ' + sys.argv[0] + ' <Google Maps API key> "From Address"  "To Address"')
        print('For example')
        print('Usage: python ' + sys.argv[
            0] + ' AJGHJ23242hBdDAXJDOSS "HashedIn Technologies, Bangalore"  "World Trade Centre, Bangalore"')
        exit(-1)

    points = get_points_along_path(sys.argv[1], sys.argv[2], sys.argv[3])
    polyline = generate_polyline(points)

    # print("List of points along the route")
    # print("------------------------------")
    # for time, geo in points.items():
    #    print(time, geo)

    # print("Polyline for this route")
    # print(polyline)
    # print("")
    # print("Hint: To visualize this route, copy the polyline and paste it in the textfield called Encoded Polyline over here - https://developers.google.com/maps/documentation/utilities/polylineutility")


