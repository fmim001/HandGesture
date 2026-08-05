"""
Improved MousePointer dengan gesture state tracking
Mencegah action execute multiple times per frame
"""

import pyautogui
import math
import time

class MousePointer:
    def __init__(self):
        self.pos_0 = None
        self.pos_1 = None
        self.sensitivity_x = 1.3
        self.sensitivity_y = 1.0
        
        # ✅ STATE TRACKING (New)
        self.last_gesture = None          # Track gesture sebelumnya
        self.gesture_start_time = None    # Kapan gesture dimulai
        self.action_executed = False      # Apakah action sudah execute?
        self.min_hold_time = 0.1          # Minimum 100ms gesture hold
        pass

    def Pointer(self, frame, hand_landmark: list):
        """Hitung posisi pointer dari landmark"""
        len_point = len(hand_landmark)
        h, w, _ = frame.shape
        option = True
        
        sum_x = sum(lm.x for lm in hand_landmark)
        sum_y = sum(lm.y for lm in hand_landmark)
        
        if len_point > 1:
            if option:
                # Rata-rata semua landmark (center of hand)
                point = (int(sum_x/len_point*w), int(sum_y/len_point*h))
            else:
                # Atau gunakan index finger tip
                point = (int(hand_landmark[8].x*w), int(hand_landmark[8].y*h))
        else:
            point = None

        return point

    def PointerMove(self, point1, point0):
        """Hitung pergerakan relatif dengan acceleration"""
        dx = point1[0] - point0[0]
        dy = point1[1] - point0[1]

        if abs(dx) < 1:
            dx = 0
        if abs(dy) < 1:
            dy = 0

        speed = math.hypot(dx, dy)

        # Acceleration curve: slow hand = 1.3x, fast hand = 2.0x
        if speed < 3:
            gain = 1.3
        elif speed < 8:
            gain = 1.8
        else:
            gain = 2.0

        dx *= self.sensitivity_x * gain
        dy *= self.sensitivity_y * gain

        return (int(dx), int(dy))
    
    def _is_gesture_held(self):
        """Check apakah gesture sudah hold cukup lama"""
        if self.gesture_start_time is None:
            return False
        
        elapsed = time.time() - self.gesture_start_time
        return elapsed >= self.min_hold_time
    
    def _on_gesture_start(self, gesture_name):
        """Dipanggil saat gesture baru terdeteksi"""
        self.last_gesture = gesture_name
        self.gesture_start_time = time.time()
        self.action_executed = False
        print(f"🎯 Gesture START: {gesture_name}")
    
    def _on_gesture_hold(self, gesture_name):
        """Dipanggil saat gesture sedang berlangsung (jangan execute)"""
        pass  # Gesture already started, just tracking
    
    def _on_gesture_end(self):
        """Dipanggil saat gesture berhenti"""
        if self.last_gesture:
            print(f"🎯 Gesture END: {self.last_gesture}")
        
        self.last_gesture = None
        self.gesture_start_time = None
        self.action_executed = False
        self.pos_0 = None
        self.pos_1 = None

    def ActionMove(self, point, gesture_name):
        """
        Main action handler dengan state tracking
        
        Flow:
        1. Gesture terdeteksi → START
        2. Gesture continue → HOLD (jangan execute lagi)
        3. Gesture hilang → END
        """
        
        # ========== GESTURE STATE MACHINE ==========
        
        if gesture_name:  # Ada gesture terdeteksi
            print(gesture_name)
            # Apakah ini gesture baru (berbeda dari sebelumnya)?
            if gesture_name != self.last_gesture:
                # Gesture baru! Execute action
                self._on_gesture_start(gesture_name)
                self._execute_gesture_action(point, gesture_name)
            
            else:
                # Gesture sama dengan sebelumnya (still holding)
                # Hanya update state, jangan execute action lagi
                self._on_gesture_hold(gesture_name)
                
                # Untuk HALO (pointer movement), terus update position
                if gesture_name == 'HALO':
                    self._on_gesture_hold_halo(point)
        
        else:  # Tidak ada gesture
            # Gesture sudah hilang
            if self.last_gesture is not None:
                self._on_gesture_end()

    def _execute_gesture_action(self, point, gesture_name):
        """Execute action berdasarkan gesture (HANYA sekali!)"""
        
        if gesture_name == 'HALO':
            # HALO: mulai tracking pointer movement
            if self.pos_0 is None:
                self.pos_0 = point
                print(f"  ├─ Start pointer tracking from {point}")
        
        elif gesture_name == 'MENUNJUK':
            # MENUNJUK: click sekali
            pyautogui.click()
            print(f"  ├─ ✓ Clicked!")
            self.action_executed = True
        
        elif gesture_name == 'PEACE':
            # PEACE: right-click sekali
            pyautogui.rightClick()
            print(f"  ├─ ✓ Right-clicked!")
            self.action_executed = True

    def _on_gesture_hold_halo(self, point):
        """Continue tracking mouse movement saat HALO hold"""
        if point is None:
            return
        
        if self.pos_0 is None:
            self.pos_0 = point
            return
        
        # Update pointer position setiap frame saat HALO active
        self.pos_1 = point
        dpos = self.PointerMove(self.pos_1, self.pos_0)
        
        # Hanya move jika ada delta yang significant
        if dpos[0] != 0 or dpos[1] != 0:
            pyautogui.moveRel(dpos[0], dpos[1])
        
        self.pos_0 = self.pos_1

# ============================================================================
# ALTERNATIVE: Gesture Debouncer (jika ingin lebih control)
# ============================================================================

class MousePointerV2:
    """Version 2: Explicit debouncing dengan cooldown"""
    
    def __init__(self):
        self.pos_0 = None
        self.pos_1 = None
        self.sensitivity_x = 1.3
        self.sensitivity_y = 1.0
        
        # Debounce settings
        self.last_action_time = {}        # {gesture_name: timestamp}
        self.debounce_delay = 0.2         # 200ms cooldown antar action
        self.halo_continuous = False      # HALO terus track, tidak debounce
    
    def Pointer(self, frame, hand_landmark: list):
        """Hitung posisi pointer dari landmark"""
        len_point = len(hand_landmark)
        h, w, _ = frame.shape
        
        sum_x = sum(lm.x for lm in hand_landmark)
        sum_y = sum(lm.y for lm in hand_landmark)
        
        if len_point > 1:
            point = (int(sum_x/len_point*w), int(sum_y/len_point*h))
        else:
            point = None
        
        return point

    def PointerMove(self, point1, point0):
        """Hitung pergerakan relatif dengan acceleration"""
        dx = point1[0] - point0[0]
        dy = point1[1] - point0[1]

        if abs(dx) < 1:
            dx = 0
        if abs(dy) < 1:
            dy = 0

        speed = math.hypot(dx, dy)

        if speed < 3:
            gain = 1.3
        elif speed < 8:
            gain = 1.8
        else:
            gain = 2.0

        dx *= self.sensitivity_x * gain
        dy *= self.sensitivity_y * gain

        return (int(dx), int(dy))
    
    def _can_execute_action(self, gesture_name):
        """Check apakah gesture boleh execute action (debounce check)"""
        
        # HALO tidak debounce, terus berjalan
        if gesture_name == 'HALO':
            return True
        
        # Gesture lain: check cooldown
        last_time = self.last_action_time.get(gesture_name, 0)
        current_time = time.time()
        elapsed = current_time - last_time
        
        if elapsed >= self.debounce_delay:
            self.last_action_time[gesture_name] = current_time
            return True
        
        return False
    
    def ActionMove(self, point, gesture_name):
        """
        Action handler dengan debounce (cooldown antar action)
        
        MENUNJUK: execute hanya 1x per 200ms
        PEACE: execute hanya 1x per 200ms
        HALO: terus berjalan (no debounce)
        """
        
        if not gesture_name:
            self.pos_0 = None
            self.pos_1 = None
            return
        
        # Check if action allowed (debounce)
        if not self._can_execute_action(gesture_name):
            return  # Still in cooldown, skip
        
        # ========== EXECUTE ACTION ==========
        
        if gesture_name == 'HALO':
            # Pointer movement (continuous)
            if self.pos_0 is None:
                self.pos_0 = point
            else:
                self.pos_1 = point
                dpos = self.PointerMove(self.pos_1, self.pos_0)
                if dpos[0] != 0 or dpos[1] != 0:
                    pyautogui.moveRel(dpos[0], dpos[1])
                self.pos_0 = self.pos_1
        
        elif gesture_name == 'MENUNJUK':
            # Click (only once per debounce period)
            pyautogui.click()
            print(f"✓ Clicked!")
        
        elif gesture_name == 'PEACE':
            # Right-click (only once per debounce period)
            pyautogui.rightClick()
            print(f"✓ Right-clicked!")