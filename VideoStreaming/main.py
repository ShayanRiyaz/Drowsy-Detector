# main.py# import the necessary packages
from flask import Flask, render_template, Response, send_from_directory, request, redirect
from flask_socketio import SocketIO
from camera import VideoCamera
import recommender
import camera
import time
import cv2
import googleMaps
import sys

sys.setrecursionlimit(5000)
timestamp_record = []

app = Flask(__name__)
socketio = SocketIO(app)
cam = VideoCamera(socket=socketio)

@app.route('/')
def index():
    # rendering webpage
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('aboutPage.html')

def gen(camera):
    global timestamp_record
    # # global tr
    start_time = time.time() #New---Code--Added
    timestamp_record.append(start_time) #New---Code--Added
    while True:
        #get camera frame
        frame = camera.get_frame(start_time,timestamp_record)
        # tr = timestamp_record
        # print(timestamp_record)
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
                
@app.route('/video_feed')
def video_feed():
    return Response(gen(cam),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/sounds/<path:filename>')
def get_sound(filename):
    return send_from_directory('/static/sounds/', filename)

@app.route('/favicon.ico')
def get_favicon():
    return send_from_directory('/static/icons/','favicon.ico')

@socketio.on('location_data')
def recieve_location(json):
    start_location = json["start_location"]
    end_location = json["end_location"]
    print(f'Start location: {start_location}, End location: {end_location}')
    # try:
    times,coords = googleMaps.simulated_user_path(start_location, end_location)
    # data = {"times": times,
    #         "coords": coords}

    data = {'data':coords}

    socketio.emit('location', data)
    # except Exception as e:
        # print("no route found")
        # socketio.emit('no_location')
        
@socketio.on('user_location')
def recieve_location(json):
    print(json)
    user_lon = json["userLon"]
    user_lat = json["userLat"]
    print(f'user lat: {user_lat} {type(user_lat)}, user_lon: {user_lon} {type(user_lon)}')
    if user_lon != 0 and user_lat != 0:
        #user_coordinates pluge here
        rc = recommender.Recommendations(user_lat, user_lon)
        dict_ = recommender.googlemaps(user_lat,user_lon)
        print(dict_.keys())
        for i in range(len(dict_['results'])):
            rc.filterType(dict_['results'][i],i)
            
        nearby_locations = rc.topRec()
        print(nearby_locations)
        data = {"data":nearby_locations}
        socketio.emit('nearby_locations', data)
    

@socketio.on('connected_event')
def handle_message(json):
    print('received json: ' + str(json))

if __name__ == '__main__':
    # defining server ip address and port
    # app.run(host='0.0.0.0',port='5000', debug=True)
    # Same utility as above but with support for sockets
    socketio.run(app, host='0.0.0.0', port='5000', debug=True)