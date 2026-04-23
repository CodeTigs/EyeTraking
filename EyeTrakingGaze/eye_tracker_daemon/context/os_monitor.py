# context/os_monitor.py
import pygetwindow as gw
import threading
import time

class OSMonitor:
    def __init__(self):
        """Inicializa o monitor em uma Thread separada (Assíncrono)."""
        self.current_window = "Iniciando..."
        self.running = True
        
        # Inicia a thread em background
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()

    def _update_loop(self):
        """Loop infinito que roda silenciosamente em background."""
        while self.running:
            try:
                window = gw.getActiveWindow()
                if window is not None and window.title != "":
                    self.current_window = window.title
                else:
                    self.current_window = "Desktop / Sem Foco"
            except Exception:
                pass
            
            # Dorme meio segundo para não sobrecarregar a CPU
            time.sleep(0.5)

    def get_active_window_title(self):
        """Retorna instantaneamente o último valor lido pela Thread."""
        return self.current_window

    def stop(self):
        """Encerra a thread ao fechar o programa."""
        self.running = False