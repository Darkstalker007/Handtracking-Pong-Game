# Hand.py
import cv2
import mediapipe as mp

class HandDetector:
    def __init__(self, maxHands=1, detectionCon=0.7, trackCon=0.5):
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

    
    
    def getIndexFingerY(self, img):
        """
        Returns the y-position (in pixels) of the tip of the index finger.
        If no hand is detected, returns None.
        """
        if self.results.multi_hand_landmarks:
            handLms = self.results.multi_hand_landmarks[0]  # Get first detected hand
            h, w, c = img.shape
            index_tip = handLms.landmark[self.mpHands.HandLandmark.INDEX_FINGER_TIP]
            y_px = int(index_tip.y * h)
            print(y_px)  # Move print before return
            return y_px
        return None

# Add main execution block
if __name__ == "__main__":
    # Initialize the webcam
    cap = cv2.VideoCapture(0)
    
    # Set camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 500)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)
    
    # Initialize hand detector
    detector = HandDetector()
    
    while True:
        success, img = cap.read()
        if not success:
            break
            
        # Find hands in the frame
        img = detector.findHands(img, draw=True)
        
        # Get index finger Y position
        y_pos = detector.getIndexFingerY(img)
        if y_pos is not None:
            cv2.putText(img, f"Y: {y_pos}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Show the image
        cv2.imshow("Hand Tracking", img)
        
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()
