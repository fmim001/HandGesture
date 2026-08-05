import cv2
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import threading

from app.detect_gesture import detect_gesture
from app.subtitle import subtitle
from app.pointer import MousePointer


ASSET_PATH = 'app/src/hand_landmarker.task'
HAND_CONNECTIONS = [
    (0,1), (1,2), (2,3), (3,4),         # Ibu jari
    (0,5), (5,6), (6,7), (7,8),         # Telunjuk
    (5,9), (9,10), (10,11), (11,12),    # Jari tengah
    (9,13), (13,14), (14,15), (15,16),  # Jari manis
    (13,17), (17,18), (18,19), (19,20), # Kelingking
    (0,17)                              # Telapak bawah
]

# ============================================================================
# GLOBAL STATE
# ============================================================================

latest_result = None
result_lock = threading.Lock()
gesture_history = []
MAX_HISTORY = 5  # Untuk smoothing gesture detection

class DetectLandmark:
    def __init__(self):
        """Main function - loop deteksi gesture"""
        self.pointer = MousePointer()
        # ========================================================================
        # 1. SETUP MEDIAPIPE HAND LANDMARKER
        # ========================================================================
        # pt = MousePointer()

        self.base_options = python.BaseOptions(model_asset_path=ASSET_PATH)
        self.options = vision.HandLandmarkerOptions(
            base_options=self.base_options,
            running_mode=vision.RunningMode.LIVE_STREAM,
            num_hands=1,  # Bisa deteksi 2 tangan sekaligus
            min_hand_detection_confidence=0.7,
            min_tracking_confidence=0.5,
            result_callback=lambda result, output_image, timestamp_ms: self.process_result(result)
        )

        self.landmarker = vision.HandLandmarker.create_from_options(self.options)



    def run(self,frame,mp_image,frame_timestamp_ms):            

        self.landmarker.detect_async(mp_image, frame_timestamp_ms)
        
            # ====================================================================
            # 4. PROCESS DETEKSI RESULTS
            # ====================================================================
            
        with result_lock:
            if latest_result and latest_result.hand_landmarks:
                hand_count = len(latest_result.hand_landmarks)
                # print(latest_result.hand_landmarks)
                for hand_idx, hand_landmarks in enumerate(latest_result.hand_landmarks):

                    point = self.pointer.Pointer(frame=frame,hand_landmark=hand_landmarks)
                    gesture_name = detect_gesture(hand_landmarks)
                    cv2.circle(frame, point, 15, (255, 255, 0), -1)
                    subtitle(frame, f"Gesture {latest_result.handedness[hand_idx][0].category_name}: {gesture_name}")

                    # A. GAMBAR SKELETON TANGAN

                    # self.draw_hand_skeleton(frame, hand_landmarks)
                    # y_offset = 90 + (hand_idx * 50)  # Offset untuk multiple hands


                return point,gesture_name
        return None,None
    
    def process_result(self,result):
        """Callback dari MediaPipe untuk menyimpan hasil deteksi"""
        global latest_result
        with result_lock:
            latest_result = result


    def draw_hand_skeleton(self,frame, hand_landmarks):
        """Gambar kerangka tangan (skeleton) pada frame"""
        h, w, _ = frame.shape
        
        # Gambar garis penghubung antar landmark
        for start_idx, end_idx in HAND_CONNECTIONS:
            x1 = int(hand_landmarks[start_idx].x * w)
            y1 = int(hand_landmarks[start_idx].y * h)
            x2 = int(hand_landmarks[end_idx].x * w)
            y2 = int(hand_landmarks[end_idx].y * h)
            
            # Garis dengan anti-aliasing
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2, cv2.LINE_AA)
        
        # Gambar titik di setiap landmark
        for lm in hand_landmarks:
            cx = int(lm.x * w)
            cy = int(lm.y * h)
            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)


    def smooth_gesture(self,gesture_name):
        """
        Smoothing gesture detection menggunakan history
        Menghindari flickering gesture yang terlalu cepat berubah
        """
        global gesture_history
        
        gesture_history.append(gesture_name)
        if len(gesture_history) > MAX_HISTORY:
            gesture_history.pop(0)
        
        # Return gesture yang paling sering muncul dalam history
        from collections import Counter
        if gesture_history:
            most_common = Counter(gesture_history).most_common(1)[0][0]
            return most_common
        return gesture_name


    def display_fps(self,frame, fps):
        """Tampilkan FPS counter pada frame"""
        if fps > 0:
            fps_text = f"FPS: {fps:.1f}"
            cv2.putText(frame, fps_text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)


