import sys
import os
import subprocess
import cv2 # Captura imagens da webcam
import numpy as np # Manipulação de imagens
import mediapipe as mp # Detecção de gestos
import pyautogui # Controle do PowerPoint
import time
from PyQt5.QtWidgets import QApplication, QWidget 
from PyQt5.QtGui import QPainter, QPen, QPixmap, QColor, QImage
from PyQt5.QtCore import Qt, QTimer

class TransparentOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Overlay de Desenho com Gestos")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()

        self.canvas = QPixmap(self.size())
        self.canvas.fill(Qt.transparent)

        self.pen_color = QColor(255, 0, 0)
        self.pen_width = 5
        self.drawing = False
        self.last_point = None

        self.modo_lapis = False
        self.modo_laser = False
        self.laser_pos = (0.0, 0.0)
        self.laser_pos_suave = (0.0, 0.0)
        self.suavizacao_laser = 0.01
        self.lapis_pos_suave = (0.0, 0.0)
        self.suavizacao_lapis = 0.01

        self.ultimo_tempo = time.time()
        self.delay_comando = 1.5  # Tempo de cooldown para comandos em segundos

        self.cap = cv2.VideoCapture(0)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=2)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)

    def dedos_levantados(self, hand_landmarks):
        dedos = []
        tips = [4, 8, 12, 16, 20]

        if hand_landmarks.landmark[tips[0]].x < hand_landmarks.landmark[tips[0] - 1].x:
            dedos.append(1)
        else:
            dedos.append(0)

        for i in range(1, 5):
            if hand_landmarks.landmark[tips[i]].y < hand_landmarks.landmark[tips[i] - 2].y:
                dedos.append(1)
            else:
                dedos.append(0)
        return dedos

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.flip(frame, 1)
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultado = self.hands.process(img_rgb)

        agora = time.time()
        cooldown_passed = (agora - self.ultimo_tempo) > self.delay_comando
        gesture_executed = False

        detected_hands_info = []
        if resultado.multi_hand_landmarks:
            for hand_landmarks_obj in resultado.multi_hand_landmarks:
                dedos = self.dedos_levantados(hand_landmarks_obj)
                total = sum(dedos)
                x = int(hand_landmarks_obj.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP].x * self.width())
                y = int(hand_landmarks_obj.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP].y * self.height())
                detected_hands_info.append({'dedos': dedos, 'total': total, 'x': x, 'y': y, 'landmarks': hand_landmarks_obj})

        if detected_hands_info:
            self.laser_pos = (float(detected_hands_info[0]['x']), float(detected_hands_info[0]['y']))

        lx, ly = self.laser_pos
        px, py = self.laser_pos_suave
        sx = int(px * self.suavizacao_laser + lx * (1 - self.suavizacao_laser))
        sy = int(py * self.suavizacao_laser + ly * (1 - self.suavizacao_laser))
        self.laser_pos_suave = (sx, sy)

        laser_toggle_gesture = False
        if len(detected_hands_info) == 1:
            primary_hand = detected_hands_info[0]
            dedos = primary_hand['dedos']
            total = primary_hand['total']
            if (total == 3 and dedos[0] == 1 and dedos[1] == 1 and dedos[2] == 1 and dedos[3] == 0 and dedos[4] == 0):
                laser_toggle_gesture = True

        if self.modo_laser:
            if cooldown_passed and laser_toggle_gesture:
                self.modo_laser = False
                self.ultimo_tempo = agora
                print("🔴 Laser DESATIVADO (Gesto de toggle)")
                gesture_executed = True

        elif self.modo_lapis:
            if detected_hands_info and cooldown_passed:
                first_hand_info = detected_hands_info[0]
                dedos = first_hand_info['dedos']
                total = first_hand_info['total']
                x = first_hand_info['x']
                y = first_hand_info['y']
                if (total == 3 and dedos[1] == 1 and dedos[2] == 1 and dedos[3] == 1 and dedos[0] == 0 and dedos[4] == 0):
                    self.modo_lapis = False
                    self.ultimo_tempo = agora
                    print("✏️ Lápis DESATIVADO")
                    self.last_point = None
                    gesture_executed = True
                else:
                    self.draw_on_canvas(x, y)
            elif not detected_hands_info:
                self.last_point = None
            else:
                self.draw_on_canvas(detected_hands_info[0]['x'], detected_hands_info[0]['y'])

        else:
            if cooldown_passed:
                num_hands_detected = len(detected_hands_info)

                if laser_toggle_gesture:
                    self.modo_laser = True
                    self.modo_lapis = False
                    self.ultimo_tempo = agora
                    print("🔴 Laser ATIVADO (Gesto de toggle)")
                    gesture_executed = True

                if not gesture_executed and num_hands_detected == 1:
                    primary_hand = detected_hands_info[0]
                    dedos = primary_hand['dedos']
                    total = primary_hand['total']

                    if total == 5 and all(d == 1 for d in dedos):
                        pyautogui.press('f5')
                        print("📺 Tela cheia ATIVADA")
                        self.ultimo_tempo = agora
                        gesture_executed = True
                    elif (total == 3 and dedos[1] == 1 and dedos[2] == 1 and dedos[3] == 1 and dedos[0] == 0 and dedos[4] == 0):
                        self.modo_lapis = True
                        self.modo_laser = False
                        self.last_point = None
                        print("✏️ Lápis ATIVADO")
                        self.ultimo_tempo = agora
                        gesture_executed = True
                    elif (total == 1 and dedos[1] == 1 and dedos[0] == 0 and dedos[2] == 0 and dedos[3] == 0 and dedos[4] == 0):
                        pyautogui.press('pagedown')
                        print("👉 Próximo slide")
                        self.ultimo_tempo = agora
                        gesture_executed = True
                    elif (total == 2 and dedos[1] == 1 and dedos[2] == 1 and dedos[0] == 0 and dedos[3] == 0 and dedos[4] == 0):
                        pyautogui.press('pageup')
                        print("👈 Slide anterior")
                        self.ultimo_tempo = agora
                        gesture_executed = True
                    elif (total == 4 and dedos[1] == 1 and dedos[2] == 1 and dedos[3] == 1 and dedos[4] == 1 and dedos[0] == 0):
                        self.canvas.fill(Qt.transparent)
                        self.update()
                        print("🧽 Rabiscos apagados")
                        self.ultimo_tempo = agora
                        gesture_executed = True
                    elif total == 0:
                        pyautogui.press('esc')
                        print("🚪 Tela cheia DESATIVADA")
                        self.ultimo_tempo = agora
                        gesture_executed = True

        self.update()

    def draw_on_canvas(self, x, y):
        x = float(x)
        y = float(y)
        if self.last_point is not None:
            x = self.last_point[0] * self.suavizacao_lapis + x * (1 - self.suavizacao_lapis)
            y = self.last_point[1] * self.suavizacao_lapis + y * (1 - self.suavizacao_lapis)

        painter = QPainter(self.canvas)
        pen = QPen(self.pen_color, self.pen_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        if self.last_point is not None:
            painter.drawLine(int(self.last_point[0]), int(self.last_point[1]), int(x), int(y))
        self.last_point = (x, y)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.canvas)
        if self.modo_laser:
            painter.setBrush(QColor(255, 0, 0))
            painter.setPen(Qt.NoPen)
            laser_size = 15
            painter.drawEllipse(
                int(self.laser_pos_suave[0]) - laser_size // 2,
                int(self.laser_pos_suave[1]) - laser_size // 2,
                laser_size, laser_size)

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

if __name__ == '__main__':
    caminho_pptx = r"C:\Users\Enzo\Desktop\Teste.pptx"
    try:
        subprocess.Popen(["start", "", caminho_pptx], shell=True)
        print("🟢 PowerPoint iniciado com o arquivo:", caminho_pptx)
    except Exception as e:
        print(f"⚠️ Erro ao abrir o PowerPoint: {e}")

    app = QApplication(sys.argv)
    overlay = TransparentOverlay()
    overlay.show()
    sys.exit(app.exec_())