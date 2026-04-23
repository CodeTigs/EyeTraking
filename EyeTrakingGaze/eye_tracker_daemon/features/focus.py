# features/focus.py
import math

class FocusDetector:
    def __init__(self, horiz_margins=(0.30, 0.70), vert_margins=(0.30, 0.70)):
        """
        Margens de tolerância. 0.5 significa que a pupila está exatamente no centro.
        Se passar de 0.70 ou cair de 0.30, o usuário desviou o olhar da tela.
        """
        self.horiz_margins = horiz_margins
        self.vert_margins = vert_margins

    def detect(self, iris_center, eye_points):
        if iris_center is None or eye_points is None:
            return False, "Sem Rosto"

        # Índices dos cantos baseados no mapeamento do MediaPipe
        p_inner = eye_points[0]
        p_outer = eye_points[8]
        p_bottom = eye_points[4]
        p_top = eye_points[12]

        # Eixo Horizontal
        dist_inner = math.hypot(iris_center[0] - p_inner[0], iris_center[1] - p_inner[1])
        dist_outer = math.hypot(iris_center[0] - p_outer[0], iris_center[1] - p_outer[1])
        ratio_h = dist_outer / (dist_inner + dist_outer) if (dist_inner + dist_outer) > 0 else 0.5

        # Eixo Vertical
        dist_top = math.hypot(iris_center[0] - p_top[0], iris_center[1] - p_top[1])
        dist_bottom = math.hypot(iris_center[0] - p_bottom[0], iris_center[1] - p_bottom[1])
        ratio_v = dist_bottom / (dist_top + dist_bottom) if (dist_top + dist_bottom) > 0 else 0.5

        is_focused = True
        status = "Focado"

        # Lógica de distração
        if ratio_h < self.horiz_margins[0] or ratio_h > self.horiz_margins[1]:
            is_focused = False
            status = "Distraido (Olhando Lado)"
        elif ratio_v < self.vert_margins[0]:
            is_focused = False
            status = "Distraido (Olhando Cima)"
        elif ratio_v > self.vert_margins[1]:
            is_focused = False
            status = "Distraido (Olhando Baixo/Celular)"

        return is_focused, status