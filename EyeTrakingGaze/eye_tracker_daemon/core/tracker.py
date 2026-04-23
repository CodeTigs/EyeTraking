# core/tracker.py
import cv2
import mediapipe as mp
import numpy as np

class GazeTracker:
    def __init__(self, max_faces=1, det_conf=0.7, track_conf=0.7):
        """
        Inicializa o rastreador ocular utilizando o MediaPipe Face Mesh.
        """
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=max_faces,
            refine_landmarks=True, # Essencial para obter os pontos precisos da íris
            min_detection_confidence=det_conf,
            min_tracking_confidence=track_conf
        )
        
        # Índices dos pontos de interesse no MediaPipe
        # O MediaPipe fornece contornos exatos para calcular EAR e a posição da pupila
        self.LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        self.RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        self.LEFT_IRIS = [474, 475, 476, 477]
        self.RIGHT_IRIS = [469, 470, 471, 472]

    def _get_coords(self, landmarks, indices, img_w, img_h):
        """Converte os landmarks normalizados para coordenadas de pixel (2D)"""
        coords = []
        for idx in indices:
            pt = landmarks[idx]
            x, y = int(pt.x * img_w), int(pt.y * img_h)
            coords.append((x, y))
        return np.array(coords)

    def process_frame(self, frame):
        """
        Processa o frame e retorna as coordenadas dos olhos, íris e ponta do nariz.
        """
        results_data = {
            "success": False,
            "left_eye": None,
            "right_eye": None,
            "left_iris": None,
            "right_iris": None,
            "iris_center_left": None,
            "iris_center_right": None,
            "nose_tip": None # <-- NOVO
        }

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        results = self.face_mesh.process(rgb_frame)
        rgb_frame.flags.writeable = True

        img_h, img_w = frame.shape[:2]

        if results.multi_face_landmarks:
            results_data["success"] = True
            face_landmarks = results.multi_face_landmarks[0].landmark

            results_data["left_eye"] = self._get_coords(face_landmarks, self.LEFT_EYE, img_w, img_h)
            results_data["right_eye"] = self._get_coords(face_landmarks, self.RIGHT_EYE, img_w, img_h)
            left_iris_coords = self._get_coords(face_landmarks, self.LEFT_IRIS, img_w, img_h)
            right_iris_coords = self._get_coords(face_landmarks, self.RIGHT_IRIS, img_w, img_h)
            
            results_data["left_iris"] = left_iris_coords
            results_data["right_iris"] = right_iris_coords

            if len(left_iris_coords) > 0 and len(right_iris_coords) > 0:
                (l_cx, l_cy), _ = cv2.minEnclosingCircle(left_iris_coords)
                (r_cx, r_cy), _ = cv2.minEnclosingCircle(right_iris_coords)
                results_data["iris_center_left"] = (int(l_cx), int(l_cy))
                results_data["iris_center_right"] = (int(r_cx), int(r_cy))
            
            # --- NOVO: Captura a ponta do nariz (Landmark 1 do MediaPipe) ---
            nose_pt = face_landmarks[1]
            results_data["nose_tip"] = (int(nose_pt.x * img_w), int(nose_pt.y * img_h))

        return results_data