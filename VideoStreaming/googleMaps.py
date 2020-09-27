import googlemaps
import pprint

API_KEY = 'AIzaSyBSDl8S2NWX5GwJHvLaQ2PMVJSSxur033Q'

gmaps = googlemaps.Client(key=API_KEY)


def googlemaps():
    # Radius is in meters, curr lat+lon is ssrt to FIU, and only checks for open locations and gas stations
    places_result = gmaps.places_nearby(location='25.751496994, -80.37333184', radius=4000, open_now=True,
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


googlemaps()
