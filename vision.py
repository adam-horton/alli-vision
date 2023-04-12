#!/usr/bin/env python3
import mediapipe as mp
import numpy as np
import cv2
from flask import Flask, Response, render_template, jsonify

HOST = '0.0.0.0'
PORT = '8000'
GATOR_BLUE_BGR = (165, 33, 0)
GATOR_ORANGE_BGR = (22, 70, 250)

class VisionApp:
        def __init__(self):
                self.hand_status = {
                                "RIGHT_HAND_RAISED" : False,
                                "LEFT_HAND_RAISED" : False,
                        }
                self.app = Flask(__name__)

        def addRoutes(self):
                self.app.add_url_rule('/', view_func=self.index)
                self.app.add_url_rule('/video_feed', view_func=self.video_feed)
                self.app.add_url_rule('/status', view_func=self.status)

        def run(self):
                self.app.run(host=HOST, port=PORT, debug=True, use_reloader=False)

        def index(self):
                return render_template('index.html')

        def video_feed(self):
                return Response(self.capture_and_detect(), mimetype = 'multipart/x-mixed-replace; boundary=frame')

        def status(self):
                if self.hand_status["LEFT_HAND_RAISED"] and self.hand_status["RIGHT_HAND_RAISED"]:
                        status_text = 'Both Hands Raised'
                elif self.hand_status["LEFT_HAND_RAISED"] and not self.hand_status["RIGHT_HAND_RAISED"]:
                        status_text = 'Left Hand Raised'
                elif not self.hand_status["LEFT_HAND_RAISED"] and self.hand_status["RIGHT_HAND_RAISED"]:
                        status_text = 'Right Hand Raised'
                else:
                        status_text = 'No Hands Raised'
                return jsonify({"status": status_text})

        def capture_and_detect(self):
                mp_drawing = mp.solutions.drawing_utils
                mp_pose = mp.solutions.pose

                cap = cv2.VideoCapture(0)
                with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
                        while True:
                                #Read in one frame
                                ret, frame = cap.read()

                                #Use mediapipe pose to process the image and determine landmarks
                                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                image.flags.writeable = False
                                results = pose.process(image)
                                image.flags.writeable = True
                                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                                try:
                                        landmarks = results.pose_landmarks.landmark
                                        self.update_status(landmarks)
                                except:
                                        pass

                                #Draw the landmarks on the image
                                mp_drawing.draw_landmarks(
                                        image,
                                        results.pose_landmarks,
                                        mp_pose.POSE_CONNECTIONS,
                                        mp_drawing.DrawingSpec(color=GATOR_ORANGE_BGR),
                                        mp_drawing.DrawingSpec(color=GATOR_BLUE_BGR)
                                        )
                                
                                #Send the frame to the live stream
                                encodedImage = cv2.imencode('.jpg', image)[1]
                                yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

        def update_status(self, landmarks):
                mp_landmark = mp.solutions.pose.PoseLandmark

                if landmarks[mp_landmark.LEFT_SHOULDER.value].y > landmarks[mp_landmark.LEFT_WRIST.value].y:
                        self.hand_status["LEFT_HAND_RAISED"] = True
                else:
                        self.hand_status["LEFT_HAND_RAISED"] = False

                if landmarks[mp_landmark.RIGHT_SHOULDER.value].y > landmarks[mp_landmark.RIGHT_WRIST.value].y:
                        self.hand_status["RIGHT_HAND_RAISED"] = True
                else:
                        self.hand_status["RIGHT_HAND_RAISED"] = False


if __name__ == "__main__":
        app = VisionApp()
        app.addRoutes()
        app.run()