#!/usr/bin/env python
# coding: utf-8

# In[3]:


from scipy.spatial import distance
from imutils import face_utils
import imutils
import dlib
import cv2
import time


# ## Readme
# #New--code--Addded are the lines I have added in current code <br>
# 
# So, for complete function of block of code I have #New-Code-Added at the start and end of the block<br>
# When there is a line added I have written just along it's Side<br>
# 
# The variables and data structure used are defined at the start of the next block, define those inside init<br>

# In[ ]:



#New---Code--Added

timestamp_record = [] #recording the timestamps in 2 mins slots
alertCount = [0] #recording within 2 mins how many times he snapped
max_thres = 8 #8 snaps of drowziness would trigger emergency alaram
time_slot_thres = 2 #time-slot 2 min
count = 0 #to slow down stream of panic recommendations
alert_flag = False
alertOccurence = 0 #count of snapped occurence

def checkSeverity(alertOccurence,start_time):
    
    end_time = time.time()
    total_time = (end_time - start_time) / 60
    next_slot = (end_time  - timestamp_record[-1]) / 60
    
    #print('Total Time Spend till now ',total_time)
    #print('Next Occurence occured within  ',next_slot)
    
    if(next_slot < time_slot_thres):
        alertCount[-1] +=1
    
    else:
        alertCount.append(1)
        timestamp_record.append(end_time)
    
    if(alertCount[-1] > max_thres or (total_time < 10 and alertOccurence >= 10)):
        print('Alert is Emergency')
    else:
        print('Give Nearby Recommendations')
        
#New---Code--Added
    

def eye_aspect_ratio(eye):

    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear
    
    
thresh = 0.25
frame_check = 15 #New--Code--Modified Make it 15 rather 20


detect = dlib.get_frontal_face_detector()
predict = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")# Dat file is the crux of the code

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]
cap=cv2.VideoCapture(0)

flag=0


start_time = time.time() #New---Code--Added
timestamp_record.append(start_time) #New---Code--Added
        
while True:
    ret, frame= cap.read()
    frame = imutils.resize(frame, width=450)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    subjects = detect(gray, 0)
    
    for subject in subjects:
        shape = predict(gray, subject)
        shape = face_utils.shape_to_np(shape)#converting to NumPy Array
        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)
        ear = (leftEAR + rightEAR) / 2.0
        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
        
        if ear < thresh:
            flag += 1
            if flag >= frame_check:
                cv2.putText(frame, "****************ALERT!****************", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame, "****************ALERT!****************", (10,325),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                alert_flag = True #New---Code--Added
            
            
        else:
            flag = 0
    
    #New---Code--Added
    if(alert_flag):
        count +=1
        
        if(count % 15 == 0):
            alertOccurence +=1
            checkSeverity(alertOccurence,start_time)
        
        alert_flag = False
    #New---Code--Added
    
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break


cv2.destroyAllWindows()
cap.release()

