import googlemaps
import pprint

API_KEY = 'AIzaSyBSDl8S2NWX5GwJHvLaQ2PMVJSSxur033Q'

gmaps = googlemaps.Client(key = API_KEY)

#Radius is in meters, curr lat+lon is ssrt to FIU, and only checks for open locations and gas stations
places_result = gmaps.places_nearby(location='25.751496994, -80.37333184', radius = 4000, open_now = True, type = 'gas_station')

#pprint.pprint(places_result)

for place in places_result['results']:
    place_id = place['place_id']
    fields = ['name', 'formatted_phone_number', 'geometry/location', 'opening_hours']
    place_details = gmaps.place(place_id = place_id, fields = fields)

    print(place_details)