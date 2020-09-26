from scipy.spatial import distance
from imutils import face_utils
import imutils
import dlib
import cv2
import time
from datetime import datetime

class VideoCamera(object):
    
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.thresh = 0.25
        self.frame_check = 20
        self.detect = dlib.get_frontal_face_detector()
        # Dat file is the crux of the code
        self.predict = dlib.shape_predictor(
            "./shape_predictor_68_face_landmarks.dat")

        (self.lStart,
         self.lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
        (self.rStart,
         self.rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]
        self.flag = 0
        self.timestamp_record = []
        
        # ## Readme
        # #New--code--Addded are the lines I have added in current code <br>
        #
        # So, for complete function of block of code I have #New-Code-Added at the start and end of the block<br>
        # When there is a line added I have written just along it's Side<br>
        #
        # The variables and data structure used are defined at the start of the next block, define those inside init<br>
        # In[ ]:
        # New---Code--Added
        self.alertCount = [0]  # recording within 2 mins how many times he snapped
        self.max_thres = 8  # 8 snaps of drowziness would trigger emergency alaram
        self.time_slot_thres = 2  # time-slot 2 min
        self.count = 0  # to slow down stream of panic recommendations
        self.alert_flag = False
        self.alertOccurence = 0  # count of snapped occurence
    
    def generateRealTimeStats(self):
 
        snaps = []
        dates = []

        def generateDateTime(seq,time): 

            nonlocal snaps,dates

            min_2 = 2*60    
            snaps = snaps + [0]*seq

            while seq > 0:
                time += min_2
                s_date = datetime.fromtimestamp(time).strftime('%y-%m-%d %a %H:%M')
                dates.append(s_date)
                seq -=1


        start = self.timestamp_record[0]

        for i in range(1,len(self.timestamp_record)):

            tf = int((self.timestamp_record[i] - start) / 60)

            if(tf <= 2):
                snaps.append(self.alertCount[i-1])
                dates.append(datetime.fromtimestamp(self.timestamp_record[i]).strftime('%y-%m-%d %a %H:%M'))
            else:
                generateDateTime(tf//2,self.timestamp_record[i-1])
                snaps[-1] = self.alerCount[i-1]


        return dates,snaps
    
    
    def __del__(self):
        self.video.release()

    def eye_aspect_ratio(self, eye):
        A = distance.euclidean(eye[1], eye[5])
        B = distance.euclidean(eye[2], eye[4])
        C = distance.euclidean(eye[0], eye[3])
        self.ear = (A + B) / (2.0 * C)
        return self.ear

    def checkSeverity(self, start_time):
        
        end_time = time.time()
        total_time = (end_time - start_time) / 60
        next_slot = (end_time - self.timestamp_record[-1]) / 60

        #print('Total Time Spend till now ',total_time)
        #print('Next Occurence occured within  ',next_slot)

        if(next_slot < self.time_slot_thres):
            self.alertCount[-1] += 1
        else:
            self.alertCount.append(1)
            self.timestamp_record.append(end_time)

        if(self.alertCount[-1] > self.max_thres or (total_time < 10 and self.alertOccurence >= 10)):
            print('Alert is Emergency')
        else:
            print('Give Nearby Recommendations')

    def get_frame(self,start_time):
        
        ret, frame = self.video.read()
        frame = imutils.resize(frame, width=450)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        start_time = time.time() #New---Code--Added
        self.timestamp_record.append(start_time) #New---Code--Added

        subjects = self.detect(gray, 0)
        for subject in subjects:
            shape = self.predict(gray, subject)
            shape = face_utils.shape_to_np(shape)  # converting to NumPy Array
            leftEye = shape[self.lStart:self.lEnd]
            rightEye = shape[self.rStart:self.rEnd]
            leftEAR = self.eye_aspect_ratio(leftEye)
            rightEAR = self.eye_aspect_ratio(rightEye)
            self.ear = (leftEAR + rightEAR) / 2.0
            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
            if self.ear < self.thresh:
                self.flag += 1
                # print(self.flag)
                if self.flag >= self.frame_check:
                    cv2.putText(frame, "****************ALERT!****************", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(frame, "****************ALERT!****************", (10, 325),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    #print ("Drowsy")
                    self.alert_flag = True  # New---Code--Added
            else:
                self.flag = 0
                
        # New---Code--Added
        if(self.alert_flag):
            self.count += 1

            if(self.count % 15 == 0):
                self.alertOccurence += 1
                self.checkSeverity(start_time)

            self.alert_flag = False
        # New---Code--Added
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
