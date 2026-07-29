import cv2
import numpy as np

def subtitle(frame : np.ndarray,text : str):
    pos = (20, 90)        # Koordinat X dan Y (posisi teks)
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 1                  # Ukuran teks
    color = (255, 255, 255)      # Putih (Format BGR: Blue=255, Green=255, Red=255)
    bg_color = (0,0,0)
    thickness = 1                # Ketebalan garis teks
    (text_width, text_height), baseline = cv2.getTextSize(text, font, scale, thickness)
    padding = 15
    
    # 3. Gambar background hitam terlebih dahulu (menggunakan koordinat pos)
    cv2.rectangle(
        frame,
        (pos[0] - padding, pos[1] - text_height - padding),          # Kiri atas kotak
        (pos[0] + text_width + padding, pos[1] + baseline + padding), # Kanan bawah kotak
        bg_color,
        thickness=cv2.FILLED                                          # Isi penuh dengan warna hitam
    )
    cv2.putText(frame, text, pos, 
                        cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness,lineType=cv2.LINE_AA)

