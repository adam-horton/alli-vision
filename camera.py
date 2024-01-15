#!/usr/bin/env python3
import mediapipe as mp
import cv2
import math
import ssl
import websockets


#################### PARAMETERS ####################

CHOMP_WINDOW = 10					# Number of frames to look back for valid chomping
MIN_CHOMP_CONFIDENCE = .8			# Minimum confidence required to detect user chomping (percentage of previous frames where user is chomping)

####################################################

#################### OTHER CONSTANTS ####################

CHOMP_ERROR = math.floor(round(CHOMP_WINDOW * (1-MIN_CHOMP_CONFIDENCE), 5))
GATOR_BLUE_BGR = (165, 33, 0)				# Gator Blue Color
GATOR_ORANGE_BGR = (22, 70, 250)			# Gator Orange Color
SERVER_URL = "WEB APPLICATION ADDRESS "		# MUST BE SETUP BEFORE RUNNING example: "ws://123.234.101.202:6003"

#########################################################

class Camera:
	def __init__(self):
		self.hand_status = {
						'RIGHT_HAND_RAISED' : False,
						'LEFT_HAND_RAISED' : False,
						'CHOMP' : False
				}
		self.previous_chomp_frame = (0, 0)
		self.valid_chomp_frames = [False for x in range(CHOMP_WINDOW)]
		self.valid_chomp_count = 0
		self.chomp_index = 0

	#################### ACCESSORS ####################

	def get_hand_status(self):
		return self.hand_status
	
	def left_hand_raised(self):
		return self.hand_status['LEFT_HAND_RAISED']
	
	def right_hand_raised(self):
		return self.hand_status['RIGHT_HAND_RAISED']
	
	def chomping(self):
		return self.hand_status['CHOMP']
			
	################################################################

	def capture_and_analyze(self, cap, pose, websocket):
		mp_drawing = mp.solutions.drawing_utils

		#Read in one frame
		ret, frame = cap.read()

		if not ret:
			return None

		# Use mediapipe pose to process the image and determine landmarks
		image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		image.flags.writeable = False
		results = pose.process(image)
		image.flags.writeable = True
		image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

		try:
			landmarks = results.pose_landmarks.landmark
			self.update_status(landmarks, websocket)
		except:
			pass

		#Draw the landmarks on the image
		mp_drawing.draw_landmarks(
				image,
				results.pose_landmarks,
				mp.solutions.pose.POSE_CONNECTIONS,
				mp_drawing.DrawingSpec(color=GATOR_ORANGE_BGR),
				mp_drawing.DrawingSpec(color=GATOR_BLUE_BGR)
				)
		
		return image


	def get_feed(self):
		mp_pose = mp.solutions.pose

		cap = cv2.VideoCapture(0)
		
		with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:

			ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
			ssl_context.check_hostname = False  # Disable hostname verification
			with websockets.connect(SERVER_URL, ssl=ssl_context) as websocket:
				print("Connected to Server")
				while(cap.isOpened()):
					
					image = self.capture_and_analyze(cap, pose, websocket)
					
					#Send the frame to the live stream
					if image is not None:
						encodedImage = cv2.imencode('.jpg', image)[1]
						yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

		cap.release()
		cv2.destroyAllWindows()

	def display_live_feed(self):
		mp_pose = mp.solutions.pose

		cap = cv2.VideoCapture(0)
		
		with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
			ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
			ssl_context.check_hostname = False  # Disable hostname verification
			with websockets.connect(SERVER_URL, ssl=ssl_context) as websocket:
				print("Connected to Server")
				while(cap.isOpened()):
					
					image = self.capture_and_analyze(cap, pose, websocket)
					
					if image is not None:
						#Show the current image
						cv2.imshow('Alli Feed', image)
		
						# Press Q on keyboard to exit
						if cv2.waitKey(1) & 0xFF == ord('q'):
							break

		cap.release()
		cv2.destroyAllWindows()


	def update_status(self, landmarks, websocket):
		mp_landmark = mp.solutions.pose.PoseLandmark

		# Chomping Logic:
		# If hands are moving apart or hands are moving towards each other in the majority of the previous frames, Set CHOMP to true
		if(self.valid_chomp_frames[self.chomp_index]):
			self.valid_chomp_count -= 1
	
		current_chomp_frame = (landmarks[mp_landmark.LEFT_WRIST.value].y, landmarks[mp_landmark.RIGHT_WRIST.value].y)
		chomp_difference = (current_chomp_frame[0] - self.previous_chomp_frame[0], current_chomp_frame[1] - self.previous_chomp_frame[1])

		if ((chomp_difference[0] > 0 and chomp_difference[1] < 0) or (chomp_difference[0] < 0 and chomp_difference[1] > 0)) \
			and (current_chomp_frame[1] < current_chomp_frame[0]):
			self.valid_chomp_count += 1
			self.valid_chomp_frames[self.chomp_index] = True
		else:
			self.valid_chomp_frames[self.chomp_index] = False 

		self.previous_chomp_frame = current_chomp_frame

		if(self.valid_chomp_count >= CHOMP_WINDOW-CHOMP_ERROR):
			self.hand_status["CHOMP"] = True
		else:
			self.hand_status["CHOMP"] = False
		
		self.chomp_index = (1 + self.chomp_index) % CHOMP_WINDOW

		# Hand Raising Logic:
		# If Wrist above shoulder set HAND_RAISED to True. Repeat for each hand
		if landmarks[mp_landmark.LEFT_SHOULDER.value].y > landmarks[mp_landmark.LEFT_WRIST.value].y:
			self.hand_status['LEFT_HAND_RAISED'] = True
		else:
			self.hand_status['LEFT_HAND_RAISED'] = False

		if landmarks[mp_landmark.RIGHT_SHOULDER.value].y > landmarks[mp_landmark.RIGHT_WRIST.value].y:
			self.hand_status['RIGHT_HAND_RAISED'] = True
		else:
			self.hand_status['RIGHT_HAND_RAISED'] = False

		websocket.send('Message') # Some logic needs to be implemented here to send the correct message to the web app


if __name__ == "__main__":
	print('Camera class: Captures video and performs Pose analysis')