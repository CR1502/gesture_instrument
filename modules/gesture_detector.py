class GestureDetector:
    def __init__(self):
        self.tip_ids = [4, 8, 12, 16, 20]

    def detect(self, landmarks, hand_label):
        fingers = []

        # Thumb
        if hand_label == "Right":
            fingers.append(landmarks[4].x < landmarks[3].x)
        else:
            fingers.append(landmarks[4].x > landmarks[3].x)

        # Other fingers
        for i in range(1, 5):
            fingers.append(landmarks[self.tip_ids[i]].y < landmarks[self.tip_ids[i] - 2].y)

        count = fingers.count(True)

        if count == 0:
            return "Fist"
        elif count == 5:
            return "Open Palm"
        else:
            return f"{count} Finger" if count == 1 else f"{count} Fingers"