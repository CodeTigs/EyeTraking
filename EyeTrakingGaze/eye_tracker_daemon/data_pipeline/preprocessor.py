# data_pipeline/preprocessor.py
import pandas as pd
import os
import glob

class DataPreprocessor:
    def __init__(self, data_dir="data", window_size="30S"):
        """
        data_dir: Pasta onde os CSVs brutos estão salvos.
        window_size: Tamanho da janela de tempo. '30S' = 30 segundos, '1Min' = 1 minuto.
        """
        self.data_dir = data_dir
        self.window_size = window_size

    def process_all_files(self):
        # Busca todos os arquivos CSV gerados pelo nosso capture.py
        all_files = glob.glob(os.path.join(self.data_dir, "*.csv"))
        
        if not all_files:
            print("Nenhum arquivo CSV encontrado na pasta data/.")
            return None

        processed_dfs = []

        for file in all_files:
            # Evita processar o arquivo final caso você rode o script duas vezes
            if "dataset_treinamento" in file:
                continue
                
            print(f"Processando: {file}")
            df = pd.read_csv(file)
            
            # Converte o timestamp (segundos) para o formato de Data/Hora (datetime)
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
            
            # Define o datetime como índice da tabela (necessário para agrupar por tempo no Pandas)
            df.set_index('datetime', inplace=True)
            
            # AGRUPAMENTO MATEMÁTICO (O Pulo do Gato)
            # Vamos fatiar os dados a cada 30 Segundos e extrair os biomarcadores
            resumo = df.resample(self.window_size).agg(
                classe=('classe', 'first'),              # A classe (TDAH/Neurotipico) é constante
                ear_medio=('ear', 'mean'),               # Média de abertura do olho (Fadiga)
                ear_minimo=('ear', 'min'),               # O quão fechado o olho chegou a ficar
                piscadas_no_bloco=('total_piscadas', lambda x: x.max() - x.min()), # Piscadas ocorridas nestes 30s
                sacadas_no_bloco=('total_sacadas', lambda x: x.max() - x.min()),   # Sácadas ocorridas nestes 30s
                trocas_janela=('janela_ativa', 'nunique') # Quantas janelas diferentes ele focou? (Distração)
            ).dropna() # Remove blocos que ficaram vazios

            # Só adiciona se o resumo tiver dados
            if not resumo.empty:
                processed_dfs.append(resumo)

        # Junta todos os blocos de todos os usuários em um super-dataset
        if processed_dfs:
            dataset_final = pd.concat(processed_dfs)
            
            # Salva o dataset final pronto para o Machine Learning
            output_path = os.path.join(self.data_dir, "dataset_treinamento.csv")
            dataset_final.to_csv(output_path, index=False)
            
            print(f"\nPré-processamento concluído com Sucesso!")
            print(f"Total de blocos de {self.window_size} gerados: {len(dataset_final)}")
            print(f"Arquivo salvo em: {output_path}")
            
            return dataset_final
        
        return None

if __name__ == "__main__":
    # Teste rápido: Você pode rodar este arquivo direto para gerar a base de treino
    print("Iniciando Pipeline de Dados...")
    preprocessor = DataPreprocessor(window_size="30S")
    dataset = preprocessor.process_all_files()
    
    if dataset is not None:
        print("\n=== AMOSTRA DOS DADOS PRONTOS PARA A I.A. ===")
        print(dataset.head())