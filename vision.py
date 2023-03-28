#!/usr/bin/env python3
import mediapipe as mp
import numpy as np
import cv2
from flask import Flask, Response, render_template, jsonify

HOST = '0.0.0.0'
PORT = '8000'
GATOR_BLUE_BGR = (165, 33, 0)
GATOR_ORANGE_BGR = (22, 70, 250)

hand_status = 'Not Initialized'

app = Flask(__name__)

@app.route('/')
def index():
        return render_template('index.html', status=hand_status)

@app.route('/video_feed')
def video_feed():
        return Response(capture_and_detect(), mimetype = 'multipart/x-mixed-replace; boundary=frame')

@app.route('/status', methods=['GET'])
def status():
        return jsonify({"status": hand_status})

def capture_and_detect():
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
                                update_status(landmarks)
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

def update_status(landmarks):
        global hand_status
        mp_landmark = mp.solutions.pose.PoseLandmark

        if landmarks[mp_landmark.LEFT_SHOULDER.value].y > landmarks[mp_landmark.LEFT_WRIST.value].y and landmarks[mp_landmark.RIGHT_SHOULDER.value].y > landmarks[mp_landmark.RIGHT_WRIST.value].y:
                hand_satus = 'Both Hands Raised'
        elif landmarks[mp_landmark.LEFT_SHOULDER.value].y > landmarks[mp_landmark.LEFT_WRIST.value].y:
                hand_status = 'Left Hand Raised'
        elif landmarks[mp_landmark.RIGHT_SHOULDER.value].y > landmarks[mp_landmark.RIGHT_WRIST.value].y:
                hand_status = 'Right Hand Raised'
        else:
                hand_status = 'Neither Hand Raised'


if __name__ == "__main__":
        app.run(host=HOST, port=PORT, debug=True, use_reloader=False)