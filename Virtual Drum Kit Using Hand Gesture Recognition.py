# Virtual Drum Kit Using Hand Gesture Recognition
import cv2
import mediapipe as mp
import pygame
import numpy as np
import time

# Initialize pygame mixer for playing drum sounds
pygame.mixer.init()
snare_sound = pygame.mixer.Sound("snare.wav")
kick_sound = pygame.mixer.Sound("kick.wav")
hihat_sound = pygame.mixer.Sound("clap.wav")

# Mediapipe setup for hand tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Set up OpenCV video capture
cap = cv2.VideoCapture(0)
width, height = 1280, 720  # Screen dimensions
cap.set(3, width)
cap.set(4, height)

# Define drum zones
drum_zones = {
    "snare": [(100, 300), (300, 500)],  # (top-left, bottom-right)
    "kick": [(500, 300), (700, 500)],
    "hihat": [(900, 300), (1100, 500)],
}

# Cooldown mechanism
cooldown_time = 0.7  # 0.5 seconds cooldown
last_played = {
    "snare": 0,
    "kick": 0,
    "hihat": 0,
}

# Function to detect if a point is inside a drum zone
def is_inside_zone(x, y, zone):
    (x1, y1), (x2, y2) = zone
    return x1 < x < x2 and y1 < y < y2

# Function to play drum sound with cooldown
def play_drum(zone_name):
    current_time = time.time()
    if current_time - last_played[zone_name] > cooldown_time:
        last_played[zone_name] = current_time
        if zone_name == "snare":
            snare_sound.play()
        elif zone_name == "kick":
            kick_sound.play()
        elif zone_name == "hihat":
            hihat_sound.play()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Flip horizontally for mirror view
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    # Draw drum zones
    for zone_name, (top_left, bottom_right) in drum_zones.items():
        color = (255, 0, 0)  # Default blue color for zones
        cv2.rectangle(frame, top_left, bottom_right, color, 2)
        cv2.putText(frame, zone_name.upper(), (top_left[0], top_left[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    # Process hand landmarks
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Get the tip of the index finger
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            x, y = int(index_finger_tip.x * width), int(index_finger_tip.y * height)

            # Check if the finger is in any drum zone
            for zone_name, zone_coords in drum_zones.items():
                if is_inside_zone(x, y, zone_coords):
                    play_drum(zone_name)

            # Draw hand landmarks
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Display the frame
    cv2.imshow("Virtual Drum Kit", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
hands.close()
pygame.mixer.quit()

