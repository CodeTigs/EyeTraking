# features/blinks.py
import numpy as np

class BlinkDetector:
    def __init__(self, ear_threshold=0.20, ear_frames=3):
        """
        ear_threshold: Valor do EAR abaixo do qual consideramos que o olho está fechado.
        ear_frames: Quantos frames consecutivos o olho precisa ficar fechado para registrar uma piscada.
        """
        self.ear_threshold = ear_threshold
        self.ear_frames = ear_frames
        self.blink_counter = 0
        self.frame_counter = 0

    def calculate_ear(self, eye_points):
        """Calcula a proporção geométrica (Altura / Largura) do olho."""
        # Separa as coordenadas X e Y
        x_coords = eye_points[:, 0]
        y_coords = eye_points[:, 1]
        
        # Calcula a largura e altura do "bounding box" do olho
        width = np.max(x_coords) - np.min(x_coords)
        height = np.max(y_coords) - np.min(y_coords)
        
        # Evita divisão por zero
        if width == 0:
            return 0.0
            
        ear = height / width
        return ear

    def detect(self, left_eye, right_eye):
        """
        Analisa o frame atual e retorna se houve uma piscada e o valor do EAR.
        """
        if left_eye is None or right_eye is None:
            return False, 0.0

        # Calcula o EAR para ambos os olhos e tira a média
        ear_left = self.calculate_ear(left_eye)
        ear_right = self.calculate_ear(right_eye)
        ear_avg = (ear_left + ear_right) / 2.0
        
        blink_detected = False

        # Verifica se o EAR está abaixo do limiar
        if ear_avg < self.ear_threshold:
            self.frame_counter += 1
        else:
            # Se o olho abriu, verifica se ele ficou fechado tempo suficiente
            if self.frame_counter >= self.ear_frames:
                self.blink_counter += 1
                blink_detected = True
            
            # Reseta o contador
            self.frame_counter = 0

        return blink_detected, ear_avg