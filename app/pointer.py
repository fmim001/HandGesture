import pyautogui
import math

class MousePointer:
    def __init__(self):
        self.pos_0 = None
        self.pos_1 = None
        self.sensitivity_x = 1.3
        self.sensitivity_y = 1.0
        pass

    def Pointer(self,frame,hand_landmark: list):
        len_point = len(hand_landmark)
        h, w, _ = frame.shape
        option = True
        sum_x = sum(lm.x for lm in hand_landmark)
        sum_y = sum(lm.y for lm in hand_landmark)
        if len_point>1:
            if option :
                point = (int(sum_x/len_point*w),int(sum_y/len_point*h))
                
            else:
                point = (int(hand_landmark[8].x*w),int(hand_landmark[8].y*h))
        else:
            point = None


        return point

    def PointerMove(self,point1,point0):
        dx = point1[0] - point0[0]
        dy = point1[1] - point0[1]

        if abs(dx) < 1:
            dx = 0
        if abs(dy)<1:
            dy= 0

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
    
    def ActionMove(self,point,gesture_name):
        if gesture_name:
            if gesture_name=='HALO':
                if self.pos_0 is None:
                    self.pos_0 = point
                else:
                    self.pos_1 = point

                    if self.pos_1 and self.pos_0:
                        dpos = self.PointerMove(self.pos_1,self.pos_0)
                        pyautogui.moveRel(dpos)

                    self.pos_0 = self.pos_1
            elif gesture_name == 'MENUNJUK' :
                pyautogui.click()
            elif gesture_name == 'PEACE' :
                pyautogui.rightClick()

        else:
            self.pos_0 = None
            self.pos_1 = None

