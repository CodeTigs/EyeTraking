# data_pipeline/logger.py
import csv
import os
import time
from datetime import datetime

class DataLogger:
    def __init__(self, output_dir="data", subject_id="voluntario_01", group="TDAH"):
        """
        Inicializa o gravador de dados.
        subject_id: Identificador anonimizado do paciente/voluntário.
        group: Classe do voluntário (ex: 'TDAH', 'Controle', 'Neurotipico').
        """
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        # Cria um nome de arquivo único baseado na data e hora
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = os.path.join(self.output_dir, f"{group}_{subject_id}_{timestamp}.csv")
        
        # Cria o arquivo e escreve o cabeçalho (as colunas do nosso banco de dados)
        with open(self.filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", 
                "classe", 
                "janela_ativa", 
                "ear", 
                "piscou", 
                "total_piscadas", 
                "amplitude_sacada", 
                "total_sacadas"
            ])
        
        self.group = group
        print(f"[Logger] Arquivo de dados criado: {self.filename}")

    def log_frame(self, janela, ear, piscou, total_piscadas, amp_sacada, total_sacadas):
        """Salva a leitura atual no arquivo CSV."""
        with open(self.filename, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                time.time(),
                self.group,
                janela,
                round(ear, 3),
                1 if piscou else 0,
                total_piscadas,
                round(amp_sacada, 2),
                total_sacadas
            ])