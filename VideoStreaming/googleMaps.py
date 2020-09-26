import googlemaps
import pprint

API_KEY = 'AIzaSyBSDl8S2NWX5GwJHvLaQ2PMVJSSxur033Q'

gmaps = googlemaps.Client(key = API_KEY)

#Radius is in meters, curr lat+lon is ssrt to FIU, and only checks for open locations and gas stations
places_result = gmaps.places_nearby(location='25.751496994, -80.37333184', radius = 40000, open_now = True, type = 'gas_station')

pprint.pprint(places_result)