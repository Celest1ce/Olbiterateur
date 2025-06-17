import cv2
import mediapipe as mp
import time
import numpy as np
import os
import platform
import sys


def get_display_resolution():
    """Return screen resolution using tkinter or pyautogui as fallback."""
    try:
        import tkinter as tk

        root = tk.Tk()
        root.withdraw()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        return width, height
    except Exception:
        try:
            import pyautogui

            size = pyautogui.size()
            return size.width, size.height
        except Exception:
            # Reasonable default if both methods fail
            return 1280, 720

# Initialisation MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2,
                       min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

def is_finger_up(landmarks, tip_id, pip_id, is_thumb=False):
    if is_thumb:
        return landmarks[tip_id].x < landmarks[pip_id].x
    return landmarks[tip_id].y < landmarks[pip_id].y

def is_only_middle_finger_up(landmarks):
    return (is_finger_up(landmarks, 12, 10) and
            not is_finger_up(landmarks, 8, 6) and
            not is_finger_up(landmarks, 4, 3, is_thumb=True) and
            not is_finger_up(landmarks, 16, 14) and
            not is_finger_up(landmarks, 20, 18))

def shutdown_computer():
    if platform.system() == "Windows":
        os.system("shutdown /s /f /t 0")
    elif platform.system() == "Linux":
        os.system("shutdown -h +1 \"Extinction déclenchée par détection de geste\"")
    elif platform.system() == "Darwin":
        os.system("osascript -e 'tell app \"System Events\" to shut down'")
    else:
        print("OS non reconnu")

def resize_with_aspect_ratio(image, target_width, target_height):
    h, w = image.shape[:2]
    scale = min(target_width / w, target_height / h)
    new_w, new_h = int(w * scale), int(h * scale)
    resized = cv2.resize(image, (new_w, new_h))

    top = (target_height - new_h) // 2
    bottom = target_height - new_h - top
    left = (target_width - new_w) // 2
    right = target_width - new_w - left

    return cv2.copyMakeBorder(resized, top, bottom, left, right, cv2.BORDER_CONSTANT)

# Fenêtre redimensionnable
window_name = 'Détection de Mains'
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 1280, 720)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    message_img = np.zeros((400, 800, 3), dtype=np.uint8)
    cv2.putText(message_img, "Aucune webcam trouv\u00E9e", (100, 220), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
    while True:
        fullscreen = cv2.getWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN)
        try:
            _, _, win_width, win_height = cv2.getWindowImageRect(window_name)
        except cv2.error:
            win_width, win_height = get_display_resolution()
            if fullscreen >= 1:
                cv2.resizeWindow(window_name, win_width, win_height)

        if fullscreen >= 1 and (win_width == 0 or win_height == 0):
            win_width, win_height = get_display_resolution()
            cv2.resizeWindow(window_name, win_width, win_height)

        resized = resize_with_aspect_ratio(message_img, win_width, win_height)
        cv2.imshow(window_name, resized)
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()
    sys.exit()

# Variables d’état
prev_time = 0
middle_finger_start_time = None
middle_finger_duration = 0
REQUIRED_DURATION = 0
countdown_started = False
shutdown_triggered = False

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Erreur: Impossible de lire la vidéo.")
        break

    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if prev_time else 0
    prev_time = curr_time

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)
    h, w = image.shape[:2]

    cv2.putText(image, f"FPS: {int(fps)}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    nb_hands = len(results.multi_hand_landmarks) if results.multi_hand_landmarks else 0
    cv2.putText(image, f"Mains: {nb_hands}", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    detected = False

    if results.multi_hand_landmarks:
        for lm in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image, lm, mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )

            if is_only_middle_finger_up(lm.landmark):
                detected = True
                tip = lm.landmark[12]
                cx, cy = int(tip.x * w), int(tip.y * h)
                cv2.circle(image, (cx, cy), 20, (0, 0, 255), -1)

    if detected:
        if middle_finger_start_time is None:
            middle_finger_start_time = time.time()
        else:
            middle_finger_duration = time.time() - middle_finger_start_time

        cv2.putText(image, "MAJEUR DETECTÉ!", (w//2 - 150, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        if middle_finger_duration >= REQUIRED_DURATION and not shutdown_triggered:
            cv2.putText(image, "EXTINCTION DU PC DANS 10 SECONDES!",
                        (w//2 - 280, h//2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            if not countdown_started:
                shutdown_computer()
                countdown_started = True
                shutdown_triggered = True
        else:
            remain = REQUIRED_DURATION - middle_finger_duration
            cv2.putText(image, f"Maintenir {remain:.1f}s pour éteindre",
                        (w//2 - 200, h//2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    else:
        middle_finger_start_time = None
        middle_finger_duration = 0

    # Resize avec conservation du ratio
    try:
        fullscreen = cv2.getWindowProperty(window_name,
                                           cv2.WND_PROP_FULLSCREEN)
        try:
            _, _, win_w, win_h = cv2.getWindowImageRect(window_name)
        except cv2.error:
            win_w, win_h = get_display_resolution()
            if fullscreen >= 1:
                cv2.resizeWindow(window_name, win_w, win_h)

        if fullscreen >= 1 and (win_w == 0 or win_h == 0):
            win_w, win_h = get_display_resolution()
            cv2.resizeWindow(window_name, win_w, win_h)

        resized = resize_with_aspect_ratio(image, win_w, win_h)
        cv2.imshow(window_name, resized)
    except cv2.error:
        break  # Fenêtre fermée manuellement => on sort proprement


    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
hands.close()
