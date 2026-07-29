"""
Deteksi Gesture Tangan Menggunakan MediaPipe Hand Landmarks
Mendukung 20+ gesture berbeda dengan logic yang terstruktur
"""

def detect_gesture(hand_landmarks):
    """
    Deteksi gesture berdasarkan posisi landmark tangan.
    
    Args:
        hand_landmarks: List dari MediaPipe hand landmarks (21 points)
    
    Returns:
        str: Nama gesture yang terdeteksi
    """
    # if handedness == "Right":
    #     thumb_open = hand_landmarks[4].x < hand_landmarks[3].x
    # else:
    #     thumb_open = hand_landmarks[4].x > hand_landmarks[3].x

    
    # ============================================================================
    # 1. HITUNG STATUS SETIAP JARI (TERBUKA/TERTUTUP)
    # ============================================================================
    
    THRESHOLD = 0.02
    
    def finger_open(tip, pip):
        return (hand_landmarks[pip].y - hand_landmarks[tip].y) > THRESHOLD

    thumb_open = hand_landmarks[4].x < hand_landmarks[3].x

    index_open = finger_open(8, 6)
    middle_open = finger_open(12, 10)
    ring_open = finger_open(16, 14)
    pinky_open = finger_open(20, 18)
    

    if (index_open and
            middle_open and
            ring_open and
            pinky_open):
            return "HALO"

    # ===============================
    # 1. KEPALAN
    # ===============================
    if (not index_open and
        not middle_open and
        not ring_open and
        not pinky_open):
        return "KEPALAN"

    # ===============================
    # 2. MENUNJUK
    # ===============================
    if (index_open and
        not middle_open and
        not ring_open and
        not pinky_open):
        return "MENUNJUK"

    # ===============================
    # 3. DUA JARI
    # ===============================
    if (index_open and
        middle_open and
        not ring_open and
        not pinky_open):
        return "PEACE"

    return "UNKNOWN"