import cv2
import json
import time
import numpy as np
import mediapipe as mp
import fluidsynth
import os

# ---------------------- LOAD CONFIG ----------------------
json_path = os.path.join(os.path.dirname(__file__), "instrument_selection.json")
with open(json_path, "r") as f:
    selected_instruments = json.load(f)

LEFT_INSTRUMENT = selected_instruments.get("left_instrument", 0)
RIGHT_INSTRUMENT = selected_instruments.get("right_instrument", 0)

# ---------------------- SETUP FLUIDSYNTH ----------------------
fs = fluidsynth.Synth()
fs.start(driver="coreaudio")  # Use 'alsa' for Linux, 'dsound' for Windows, 'coreaudio' for Mac

soundfont_path = os.path.join(os.path.dirname(__file__), "assets", "FluidR3_GM", "FluidR3_GM.sf2")
soundfont_id = fs.sfload(soundfont_path)
fs.program_select(0, soundfont_id, 0, LEFT_INSTRUMENT)
fs.program_select(1, soundfont_id, 0, RIGHT_INSTRUMENT)

# ---------------------- GESTURE MAPPING ----------------------
gesture_to_chord = {
    "Open Palm": ["G", "B", "D"],      # G major
    "Fist": [],                        # Stop
    "1 Fingers": ["C", "E", "G"],      # C major
    "2 Fingers": ["D", "F", "A"],      # D minor
    "3 Fingers": ["E", "G", "B"],      # E minor
    "4 Fingers": ["F", "A", "C"],      # F major
}

note_mapping = {
    "C": 60, "D": 62, "E": 64,
    "F": 65, "G": 67, "A": 69, "B": 71
}

def chord_to_midi(chord):
    return [note_mapping[n] for n in chord if n in note_mapping]

# ---------------------- MEDIAPIPE SETUP ----------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2)
mp_drawing = mp.solutions.drawing_utils

# ---------------------- TRACKING STATE ----------------------
current_notes = {"Left": [], "Right": []}
previous_gestures = {"Left": None, "Right": None}

def detect_gesture(hand_landmarks):
    if hand_landmarks is None:
        return "None"
    tip_ids = [4, 8, 12, 16, 20]
    fingers = []

    # Thumb
    fingers.append(hand_landmarks.landmark[tip_ids[0]].x < hand_landmarks.landmark[tip_ids[0] - 1].x)
    # Other fingers
    for i in range(1, 5):
        fingers.append(hand_landmarks.landmark[tip_ids[i]].y < hand_landmarks.landmark[tip_ids[i] - 2].y)

    total = fingers.count(True)

    if total == 0:
        return "Fist"
    elif total == 5:
        return "Open Palm"
    else:
        return f"{total} Fingers"

# ---------------------- MAIN LOOP ----------------------
cap = cv2.VideoCapture(0)
while True:
    success, frame = cap.read()
    if not success:
        break

    flipped_frame = cv2.flip(frame, 1)
    image = cv2.cvtColor(flipped_frame, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    # Flip for mirrored user display
    display_frame = cv2.flip(frame.copy(), 1)

    # Track visible hands
    visible_hands = {"Left": False, "Right": False}

    if results.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            raw_label = results.multi_handedness[idx].classification[0].label  # 'Left' or 'Right'
            label = "Left" if raw_label == "Right" else "Right"
            visible_hands[label] = True

            gesture = detect_gesture(hand_landmarks)
            print(f"🖐 {label} detected gesture: {gesture}")

            if gesture != previous_gestures[label]:
                # Stop previous notes
                for note in current_notes[label]:
                    fs.noteoff(0 if label == "Left" else 1, note)
                current_notes[label] = []

                if gesture in gesture_to_chord:
                    chord = chord_to_midi(gesture_to_chord[gesture])
                    for note in chord:
                        fs.noteon(0 if label == "Left" else 1, note, 100)
                    current_notes[label] = chord
                    print(f"🎵 Playing chord {gesture_to_chord[gesture]} for {label} ({gesture})")
                elif gesture == "Fist":
                    print(f"Stopping chord for {label} (Fist detected)")
                else:
                    print(f"⚠️ No chord mapped for gesture: {gesture}")

                previous_gestures[label] = gesture

            mp_drawing.draw_landmarks(display_frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Stop notes if hand disappeared
    for hand in ["Left", "Right"]:
        if not visible_hands[hand] and current_notes[hand]:
            for note in current_notes[hand]:
                fs.noteoff(0 if hand == "Left" else 1, note)
            current_notes[hand] = []
            previous_gestures[hand] = None
            print(f"✋ No {hand} hand detected — stopping notes.")

    cv2.imshow("Gesture Instrument", display_frame)
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
fs.delete()
cv2.destroyAllWindows()