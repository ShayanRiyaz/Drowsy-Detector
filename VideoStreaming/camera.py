from scipy.spatial import distance
from imutils import face_utils
import imutils
import dlib
import cv2

class VideoCamera(object):
	def __init__(self):
		self.video = cv2.VideoCapture(0)
		self.thresh = 0.25
		self.frame_check = 20
		self.detect = dlib.get_frontal_face_detector()
		self.predict = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat") # Dat file is the crux of the code

		(self.lStart, self.lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
		(self.rStart, self.rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]
		self.flag=0

	def __del__(self):
		self.video.release()


	def eye_aspect_ratio(self,eye):
		A = distance.euclidean(eye[1], eye[5])
		B = distance.euclidean(eye[2], eye[4])
		C = distance.euclidean(eye[0], eye[3])
		self.ear = (A + B) / (2.0 * C)
		return self.ear
	

	def get_frame(self):
		ret, frame=self.video.read()
		frame = imutils.resize(frame, width=450)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		subjects = self.detect(gray, 0)
		for subject in subjects:
			shape = self.predict(gray, subject)
			shape = face_utils.shape_to_np(shape)#converting to NumPy Array
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
				#print(self.flag)
				if self.flag >= self.frame_check:
					cv2.putText(frame, "****************ALERT!****************", (10, 30),
						cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
					cv2.putText(frame, "****************ALERT!****************", (10,325),
						cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
					#print ("Drowsy")
			else:
				self.flag = 0
		#cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF
		ret,jpeg = cv2.imencode('.jpg',frame)
		return jpeg.tobytes()
