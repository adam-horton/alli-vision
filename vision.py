#!/usr/bin/env python3
import mediapipe as mp
import numpy as np
import cv2

def main():
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        mp_pose = mp.solutions.pose

        cap = cv2.VideoCapture(0)
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
                while cap.isOpened():
                        ret, frame = cap.read()

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
                        cv2.imshow('Mediapipe Feed', image)

                        if cv2.waitKey(10) & 0xFF == ord('q'):
                                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
        main()