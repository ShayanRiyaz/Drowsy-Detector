# main.py# import the necessary packages
from flask import Flask, render_template, Response, send_from_directory
from flask_socketio import SocketIO
from camera import VideoCamera
import camera
import time
import cv2

#timestamp_record = []

app = Flask(__name__)


@app.route('/')
def index():
    # rendering webpage
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('aboutPage.html')
    
def gen(camera):
    #start_time = time.time() #New---Code--Added
    #timestamp_record.append(start_time) #New---Code--Added
    while True:
        #get camera frame
        frame = camera.get_frame()#start_time,timestamp_record)
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
                
@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/sounds/<path:filename>')
def get_sound(filename):
    return send_from_directory('/static/sounds/', filename)

if __name__ == '__main__':
    # defining server ip address and port
    app.run(host='0.0.0.0',port='5000', debug=True)