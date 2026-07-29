from app.landmark_detect import DetectLandmark
from app.pointer import MousePointer

import cv2
import time
import mediapipe as mp

import pyautogui

VIDEO_PATH = 'app/src/DUMMY_VIDEO.mp4'
USE_WEBCAM = False  # Set False untuk menggunakan video file
FPS_DISPLAY = True  # Tampilkan FPS counter



class MyApp:
    def __init__(self):
        self.hand = DetectLandmark()
        self.pointer = MousePointer()
        # self.mouse = pyautogui
        pass        

    def main(self):     

        if USE_WEBCAM:
            cap = cv2.VideoCapture(0)
            print("📷 Menggunakan Webcam...")
        else:
            cap = cv2.VideoCapture(VIDEO_PATH)
            print(f"🎬 Membaca video dari: {VIDEO_PATH}")
        
        if not cap.isOpened():
            print("❌ Error: Tidak bisa membuka video/webcam")
            return
        
        # Set property kamera untuk performa lebih baik
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer untuk latency lebih rendah
        cap.set(cv2.CAP_PROP_FPS, 30)  # Target 30 FPS
        
        # ========================================================================
        # 3. MAIN LOOP
        # ========================================================================
        
        frame_count = 0
        start_time = time.time()
        fps = 0
        pos_0 = None
        pos_1 = None

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("⚠️  Video selesai atau error membaca frame")
                break
            
            # Flip frame untuk efek mirror (webcam)
            frame = cv2.flip(frame, 1)
            
            # Convert BGR to RGB untuk MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            # Deteksi async (LIVE_STREAM mode)
            frame_timestamp_ms = int(time.time() * 1000)

            point,gesture_name = self.hand.run(frame,mp_image,frame_timestamp_ms)
            if point and gesture_name:
                self.pointer.ActionMove(point,gesture_name)
                
                
            if  USE_WEBCAM:
                display_frame = cv2.resize(frame, (540,960))
                cv2.imshow('Deteksi Gesture Tangan (MediaPipe)', display_frame)
            else:
                cv2.imshow('Deteksi Gesture Tangan (MediaPipe)', frame)
            
            # ====================================================================
            # 6. INPUT HANDLING
            # ====================================================================
            
            key = cv2.waitKey(5) & 0xFF
            if key == ord('q'):
                print("\n👋 Keluar dari program...")
                break
            # elif key == ord('r'):
            #     gesture_history.clear()
            #     print("🔄 History gesture direset")
            elif key == ord('s'):
                # Screenshot
                filename = f"gesture_screenshot_{int(time.time())}.png"
                cv2.imwrite(filename, frame)
                print(f"📸 Screenshot tersimpan: {filename}")

            # ========================================================================
            # CLEANUP
            # ========================================================================
            
        cap.release()
        cv2.destroyAllWindows()
        print("✅ Program selesai")

        return None
        