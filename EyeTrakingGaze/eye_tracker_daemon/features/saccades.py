# features/saccades.py
import math

class SaccadeDetector:
    def __init__(self, amplitude_threshold=5.5):
        self.amplitude_threshold = amplitude_threshold
        self.prev_iris_pos = None
        self.prev_anchor_pos = None
        self.saccade_counter = 0

    def detect(self, current_iris_pos, current_eye_points):
        """
        Calcula o movimento da íris compensando o movimento do rosto
        usando o canto interno do olho como âncora fixa.
        """
        if current_iris_pos is None or current_eye_points is None:
            self.prev_iris_pos = None
            self.prev_anchor_pos = None
            return False, 0.0

        # O índice 0 no MediaPipe para o olho esquerdo é o canto interno.
        current_anchor_pos = current_eye_points[0]

        saccade_detected = False
        amplitude = 0.0

        if self.prev_iris_pos is not None and self.prev_anchor_pos is not None:
            # 1. Movimento de arrasto da cabeça (canto do olho)
            dx_anchor = current_anchor_pos[0] - self.prev_anchor_pos[0]
            dy_anchor = current_anchor_pos[1] - self.prev_anchor_pos[1]

            # 2. Movimento bruto da íris
            dx_iris = current_iris_pos[0] - self.prev_iris_pos[0]
            dy_iris = current_iris_pos[1] - self.prev_iris_pos[1]

            # 3. Movimento Real (Limpo do arrasto da cabeça)
            dx_true = dx_iris - dx_anchor
            dy_true = dy_iris - dy_anchor
            
            amplitude = math.hypot(dx_true, dy_true)

            if amplitude > self.amplitude_threshold:
                saccade_detected = True
                self.saccade_counter += 1

        self.prev_iris_pos = current_iris_pos
        self.prev_anchor_pos = current_anchor_pos

        return saccade_detected, amplitude