#!/usr/bin/env python3
import mediapipe as mp
import numpy as np
import cv2
from flask import Response
from flask import Flask
from flask import render_template

HOST = '100.65.29.50' #FIXME
PORT = '8000'

app = Flask(__name__)

@app.route('/')
def index():
        return render_template('index.html')

@app.route('/video_feed')
def video_feed():
        return Response(capture_and_detect, mimetype = 'multipart/x-mixed-replace; boundary=frame')

def capture_and_detect():
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        mp_pose = mp.solutions.pose

        cap = cv2.VideoCapture(0)
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
                while cap.isOpened():
                        #Read in one frame
                        ret, frame = cap.read()

                        #Use mediapipe to compute and draw overlay
                        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        image.flags.writeable = False
                        results = pose.process(image)
                        image.flags.writeable = True
                        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                        mp_drawing.draw_landmarks(
                                image,
                                results.pose_landmarks,
                                mp_pose.POSE_CONNECTIONS,
                                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
                        
                        #Send the frame to the live stream
                        encodedImage = cv2.imencode('.jpg', image)
                        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
                        
                        #Display the image on the screen
                        cv2.imshow('Mediapipe Feed', image)

                        #Wait 1ms, if q is pressed, quit
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
        app.run(host=HOST, port=PORT, debug=True, use_reloader=False)