# features/focus.py
import math

class FocusDetector:
    def __init__(self, horiz_margins=(0.40, 0.60), vert_margins=(0.40, 0.60), smoothing=0.2):
        """
        horiz_margins: Voltei para 0.40 e 0.60 (bom equilíbrio com o filtro).
        smoothing: Fator de amortecimento (0.0 a 1.0). 
                    - 0.1 = Demora para responder (muito suave).
                    - 0.9 = Responde super rápido (quase sem filtro).
                    - 0.2 é o padrão ouro para 30 FPS.
        """
        self.horiz_margins = horiz_margins
        self.vert_margins = vert_margins
        self.smoothing = smoothing
        
        # Variáveis que guardam o histórico suavizado
        self.smooth_ratio_h = 0.5
        self.smooth_ratio_v = 0.5

    def detect(self, iris_center, eye_points):
        if iris_center is None or eye_points is None:
            return False, "Fuga de Tela (Rosto Ausente)"

        p_inner = eye_points[0]
        p_outer = eye_points[8]
        p_bottom = eye_points[4]
        p_top = eye_points[12]

        # 1. Calcula a proporção crua e ruidosa
        dist_inner = math.hypot(iris_center[0] - p_inner[0], iris_center[1] - p_inner[1])
        dist_outer = math.hypot(iris_center[0] - p_outer[0], iris_center[1] - p_outer[1])
        raw_ratio_h = dist_outer / (dist_inner + dist_outer) if (dist_inner + dist_outer) > 0 else 0.5

        dist_top = math.hypot(iris_center[0] - p_top[0], iris_center[1] - p_top[1])
        dist_bottom = math.hypot(iris_center[0] - p_bottom[0], iris_center[1] - p_bottom[1])
        raw_ratio_v = dist_bottom / (dist_top + dist_bottom) if (dist_top + dist_bottom) > 0 else 0.5

        # 2. O PULO DO GATO: Aplica a Média Móvel Exponencial
        self.smooth_ratio_h = (raw_ratio_h * self.smoothing) + (self.smooth_ratio_h * (1.0 - self.smoothing))
        self.smooth_ratio_v = (raw_ratio_v * self.smoothing) + (self.smooth_ratio_v * (1.0 - self.smoothing))

        is_focused = True
        status = "Foco Central"

        # 3. Toma a decisão usando o dado filtrado/suavizado
        if self.smooth_ratio_h < self.horiz_margins[0] or self.smooth_ratio_h > self.horiz_margins[1]:
            is_focused = False
            status = "Fuga de Borda (Lado)"
        elif self.smooth_ratio_v < self.vert_margins[0]:
            is_focused = False
            status = "Fuga de Borda (Cima)"
        elif self.smooth_ratio_v > self.vert_margins[1]:
            is_focused = False
            status = "Fuga de Borda (Baixo)"
       # print(f"Lendo -> Horizontal: {self.smooth_ratio_h:.2f} | Vertical: {self.smooth_ratio_v:.2f}")
        return is_focused, status