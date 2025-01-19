import cv2
import mediapipe as mp
import pyautogui
import time

# Inisialisasi Mediapipe dan PyAutoGUI
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Menonaktifkan fitur fail-safe PyAutoGUI
pyautogui.FAILSAFE = False

# Fungsi untuk menghitung jarak antara dua titik
def calculate_distance(point1, point2):
    return ((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2) ** 0.5

# Fungsi untuk menginterpolasi posisi mouse
def smooth_move(start_pos, end_pos, duration):
    steps = int(duration * 30)  # jumlah langkah interpolasi, 30 langkah per detik
    x_steps = (end_pos[0] - start_pos[0]) / steps
    y_steps = (end_pos[1] - start_pos[1]) / steps

    for i in range(steps):
        pyautogui.moveTo(start_pos[0] + x_steps * i, start_pos[1] + y_steps * i)
        time.sleep(duration / steps)

# Buka kamera
cap = cv2.VideoCapture(0)

prev_x, prev_y = 0, 0  # Variabel untuk menyimpan posisi mouse sebelumnya

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        continue

    # Membalikkan frame agar sesuai dengan orientasi mirror
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Ambil koordinat jari
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            ring_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]

            # Pemetaan koordinat dari frame ke layar
            screen_width, screen_height = pyautogui.size()
            x = int(index_finger_tip.x * screen_width)
            y = int(index_finger_tip.y * screen_height)

            # Menggerakkan mouse dengan interpolasi posisi
            smooth_move((prev_x, prev_y), (x, y), 0.1)
            prev_x, prev_y = x, y

            # Hitung jarak antara ujung jari telunjuk dan ibu jari
            distance_thumb_index = calculate_distance(index_finger_tip, thumb_tip)
            # Hitung jarak antara ujung jari telunjuk dan tengah
            distance_index_middle = calculate_distance(index_finger_tip, middle_finger_tip)
            # Hitung jarak antara ujung jari manis dan tengah
            distance_ring_middle = calculate_distance(ring_finger_tip, middle_finger_tip)

            # Debugging
            print(f'Distance Thumb-Index: {distance_thumb_index}')
            print(f'Distance Index-Middle: {distance_index_middle}')
            print(f'Distance Ring-Middle: {distance_ring_middle}')

            # Logika untuk klik
            if distance_thumb_index < 0.05:
                pyautogui.click()

            # Logika untuk scroll ke atas
            if distance_index_middle < 0.05 and index_finger_tip.y < middle_finger_tip.y:
                pyautogui.scroll(10)
                print("Scrolling up")

            # Logika untuk scroll ke bawah
            if distance_ring_middle < 0.05 and ring_finger_tip.y < middle_finger_tip.y:
                pyautogui.scroll(-10)
                print("Scrolling down")

    cv2.imshow('Hand Tracking', frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
