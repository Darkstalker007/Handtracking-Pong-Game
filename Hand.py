# Hand.py
import cv2
import mediapipe as mp

class HandDetector:
    def __init__(self, maxHands=1, detectionCon=0.7, trackCon=0.7):
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=False):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def getIndexFingerX(self, img):
        """
        Returns the x-position (in pixels) of the tip of the index finger.
        If no hand is detected, returns None.
        """
        if self.results.multi_hand_landmarks:
            handLms = self.results.multi_hand_landmarks[0]
            h, w, _ = img.shape
            index_tip = handLms.landmark[self.mpHands.HandLandmark.INDEX_FINGER_TIP]
            return int(index_tip.x * w)
        return None