import cv2
import speech_recognition as sr
import os
import pyautogui
import time
from gtts import gTTS
import pygame
from pygame import mixer
from time import sleep

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Katakan sesuatu...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("Memahami...")
        text = recognizer.recognize_google(audio, language="id-ID")
        return text.lower() if text else None
    except sr.UnknownValueError:
        print("Maaf, saya tidak dapat memahami suara Anda.")
        return None
    except sr.RequestError as e:
        print(f"Terjadi kesalahan pada permintaan ke layanan Google: {e}")
        return None

def speak(text):
    if text is not None:
        bahasa = 'id'
        ucapan = gTTS(text=text, lang=bahasa, slow=False)
        ucapan.save("response.mp3")

        pygame.init()
        mixer.init()

        try:
            mixer.music.load("response.mp3")
            mixer.music.play()
            while pygame.mixer.music.get_busy():
                sleep(1)
        finally:
            mixer.quit()
            os.remove("response.mp3")

def open_application(app_name):
    speak(f"Membuka {app_name}...")
    pyautogui.hotkey("winleft")
    time.sleep(1)
    pyautogui.write(app_name)
    pyautogui.press("enter")

def close_application(app_name):
    speak(f"Menutup {app_name}...")
    os.system(f"TASKKILL /F /IM {app_name}.exe")

def capture_face_and_show():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)  # 0 menunjukkan kamera default, ganti dengan 1 atau 2 jika Anda memiliki lebih dari satu kamera

    while True:
        ret, frame = cap.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(frame, 'Wajah Terdeteksi!', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

            face_image = frame[y:y + h, x:x + w]
            cv2.imwrite("wajah_saya.jpg", face_image)
            print("Foto wajah Anda telah diambil.")

            # Menampilkan wajah yang diambil
            cv2.imshow('Wajah Saya', face_image)
            cv2.waitKey(0)  # Tunggu sampai pengguna menekan tombol apa pun

            cap.release()
            cv2.destroyAllWindows()
            return

        cv2.imshow('Deteksi Wajah', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def jarvis_response(command):
    if "halo" in command:
        return "Halo, ada yang bisa saya bantu?"
    elif "henti" in command:
        return "Program dihentikan. Sampai jumpa!"
    elif "buka kamera" in command:
        speak("Katakan sesuatu...")
        speak("Memahami...")
        capture_face_and_show()
        speak("Foto wajah Anda telah diambil.")
        return
    elif "buka" in command:
        app_name = command.replace("buka", "").strip()
        open_application(app_name)
        return f"Oke, membuka {app_name}."
    elif "tutup" in command:
        app_name = command.replace("tutup", "").strip()
        close_application(app_name)
        return f"Oke, menutup {app_name}."

def main():
    welcome_text = "Halo, selamat datang, saya adalah robot anda"
    speak(welcome_text)

    while True:
        speak("Katakan sesuatu...")
        command = recognize_speech()

        if command is not None:
            speak("Memahami...")
            response = jarvis_response(command)

            print("Anda berkata:", command)
            print("Jarvis menjawab:", response)
            speak(response)

            if "henti" in command:
                speak("Program dihentikan. Sampai jumpa!")
                break
        else:
            print("Tidak ada teks yang terdeteksi.")

if __name__ == "__main__":
    main()
