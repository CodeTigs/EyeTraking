# core/capture.py
import cv2
import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.blinks import BlinkDetector
from features.saccades import SaccadeDetector
from context.os_monitor import OSMonitor
from core.tracker import GazeTracker
from data_pipeline.logger import DataLogger

class CameraCapture:
    def __init__(self, device_id=0, width=640, height=480, fps=30):
        self.device_id = device_id
        self.width = width
        self.height = height
        self.fps = fps
        self.cap = None

    def start(self):
        self.cap = cv2.VideoCapture(self.device_id, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        if not self.cap.isOpened():
            raise RuntimeError(f"Erro ao abrir a câmera com ID {self.device_id}.")

    def read_frame(self):
        if self.cap is None or not self.cap.isOpened():
            return False, None
        return self.cap.read()

    def stop(self):
        if self.cap is not None:
            self.cap.release()

# ==========================================
# INTERFACE GRÁFICA INICIAL (TKINTER)
# ==========================================
def show_startup_gui():
    """Exibe uma interface para coletar o nome e o grupo do voluntário antes de iniciar."""
    user_data = {"subject_id": None, "group": None}

    def on_start():
        nome = entry_nome.get().strip()
        grupo = combo_grupo.get()
        
        if not nome:
            messagebox.showwarning("Aviso", "Por favor, insira o nome do voluntário.")
            return
            
        # Formata o nome para evitar problemas no nome do arquivo (tira espaços)
        nome_formatado = nome.replace(" ", "_").lower()
            
        user_data["subject_id"] = nome_formatado
        user_data["group"] = grupo
        root.destroy() # Fecha a janela e permite que o código continue

    def on_cancel():
        root.destroy()
        sys.exit(0) # Encerra o programa completamente

    root = tk.Tk()
    root.title("Eye Tracking - Coleta de Dados")
    root.geometry("350x250")
    root.resizable(False, False)
    
    # Centraliza a janela na tela
    root.eval('tk::PlaceWindow . center')

    # Estilo
    style = ttk.Style()
    style.theme_use('clam')

    # Elementos da Interface
    ttk.Label(root, text="Configuração do Voluntário", font=("Arial", 14, "bold")).pack(pady=15)

    ttk.Label(root, text="Nome do Voluntário:").pack(anchor="w", padx=30)
    entry_nome = ttk.Entry(root, width=30)
    entry_nome.pack(pady=5, padx=30)

    ttk.Label(root, text="Grupo / Diagnóstico:").pack(anchor="w", padx=30, pady=(10, 0))
    combo_grupo = ttk.Combobox(root, values=["Neurotipico", "TDAH"], state="readonly", width=27)
    combo_grupo.current(0) # Define "Neurotipico" como padrão
    combo_grupo.pack(pady=5, padx=30)

    # Botões
    frame_botoes = ttk.Frame(root)
    frame_botoes.pack(pady=20)
    
    ttk.Button(frame_botoes, text="Iniciar Coleta", command=on_start).pack(side="left", padx=10)
    ttk.Button(frame_botoes, text="Cancelar", command=on_cancel).pack(side="right", padx=10)

    root.protocol("WM_DELETE_WINDOW", on_cancel) # Trata o clique no 'X' da janela
    root.mainloop()

    return user_data["subject_id"], user_data["group"]

# ==========================================
# LOOP PRINCIPAL DO APLICATIVO
# ==========================================
if __name__ == "__main__":
    # 1. Chama a interface gráfica primeiro e trava a execução até o usuário preencher
    subject_id, group = show_startup_gui()
    
    if not subject_id:
        sys.exit(0)

    print(f"Iniciando captura para: {subject_id} (Grupo: {group})")
    
    # 2. Inicializa a câmera
    cam = CameraCapture(device_id=0) # Mude para 1 se necessário
    try:
        cam.start()
    except RuntimeError as e:
        print(e)
        sys.exit(1)
        
    # 3. Inicializa os módulos
    tracker = GazeTracker()
    blink_detector = BlinkDetector(ear_threshold=0.20, ear_frames=1)
    saccade_detector = SaccadeDetector(amplitude_threshold=2.9) 
    os_monitor = OSMonitor()
    
    # 4. Inicializa o Gravador de Dados com os dados preenchidos na interface
    logger = DataLogger(subject_id=subject_id, group=group)

    while True:
        ret, frame = cam.read_frame()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        janela_ativa = os_monitor.get_active_window_title()
        results = tracker.process_frame(frame)

        if results["success"]:
            # Desenhos do MediaPipe
            if results["left_eye"] is not None:
                cv2.polylines(frame, [results["left_eye"]], isClosed=True, color=(0, 255, 0), thickness=1)
            if results["right_eye"] is not None:
                cv2.polylines(frame, [results["right_eye"]], isClosed=True, color=(0, 255, 0), thickness=1)
            if results["left_iris"] is not None:
                cv2.polylines(frame, [results["left_iris"]], isClosed=True, color=(0, 255, 255), thickness=1)
                cv2.circle(frame, results["iris_center_left"], 2, (0, 0, 255), -1)
            if results["right_iris"] is not None:
                cv2.polylines(frame, [results["right_iris"]], isClosed=True, color=(0, 255, 255), thickness=1)
                cv2.circle(frame, results["iris_center_right"], 2, (0, 0, 255), -1)

            # Análise
            piscou, ear_atual = blink_detector.detect(results["left_eye"], results["right_eye"])
            cv2.putText(frame, f"EAR: {ear_atual:.2f} | Piscadas: {blink_detector.blink_counter}", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            if ear_atual > (blink_detector.ear_threshold + 0.02):
                deu_salto, amplitude = saccade_detector.detect(results["iris_center_left"], results["left_eye"])
                cv2.putText(frame, f"Sacadas: {saccade_detector.saccade_counter} | Amp Real: {amplitude:.1f}px", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
            else:
                saccade_detector.prev_iris_pos = None
                saccade_detector.prev_anchor_pos = None
                amplitude = 0.0
                cv2.putText(frame, f"Sacadas: {saccade_detector.saccade_counter} | Amp Real: 0.0px (Piscando)", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)

            janela_texto = janela_ativa[:30] + "..." if len(janela_ativa) > 30 else janela_ativa
            cv2.putText(frame, f"App: {janela_texto}", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)

            # Grava no CSV usando o nome que veio da interface!
            logger.log_frame(
                janela=janela_ativa, 
                ear=ear_atual, 
                piscou=piscou, 
                total_piscadas=blink_detector.blink_counter, 
                amp_sacada=amplitude, 
                total_sacadas=saccade_detector.saccade_counter
            )

        cv2.imshow("Teste MediaPipe - Gaze Tracker", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    os_monitor.stop()
    cam.stop()
    cv2.destroyAllWindows()
