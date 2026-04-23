# EyeTrackingGaze - ADHD Behavioral Analysis 🧠👁️

Este projeto consiste em um sistema de rastreamento ocular (Eye Tracking) desenvolvido em Python para a extração de biomarcadores comportamentais (piscadas, sácadas e zonas de foco). O objetivo principal é fornecer dados estruturados para o treinamento de modelos de Machine Learning focados no auxílio ao diagnóstico de TDAH (Transtorno de Déficit de Atenção com Hiperatividade).

## 🚀 Funcionalidades Atuais

- **Detecção de Piscadas (Blinks):** Cálculo de EAR (*Eye Aspect Ratio*) em tempo real via MediaPipe.
- **Rastreamento de Sácadas:** Detecção de movimentos rápidos dos olhos com compensação de movimento da cabeça (usando o canto interno do olho como âncora geométrica).
- **Monitoramento de Contexto (OS Monitor):** Identificação da janela ativa no Sistema Operacional em Thread separada para evitar gargalos de FPS.
- **Zonas de Atenção (Focus Detector):** Classificação do olhar em *Foco Central*, *Fuga de Borda* ou *Fuga de Tela*, utilizando filtros de suavização (EMA) para eliminar ruídos de leitura.
- **Data Pipeline:** Exportação automática de logs estruturados em formato CSV para análise de dados e treinamento de IA.
- **Interface de Coleta:** GUI em Tkinter para identificação de voluntários e grupos (TDAH vs Neurotípico) antes do início dos testes.

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.10+
- **Visão Computacional:** OpenCV, MediaPipe
- **Manipulação de Dados:** Pandas, Numpy
- **Interface Gráfica:** Tkinter
- **Monitoramento de Sistema:** PyGetWindow

## 📂 Estrutura do Projeto

```text
eye_tracker_daemon/
├── core/
│   ├── capture.py        # Loop principal e integração da câmera
│   └── tracker.py        # Wrapper do MediaPipe Face Mesh
├── features/
│   ├── blinks.py         # Lógica de detecção de piscadas
│   ├── saccades.py       # Algoritmo de sácadas compensadas
│   └── focus.py          # Classificador de zonas de atenção
├── context/
│   └── os_monitor.py     # Monitor de janelas ativas (Threaded)
├── data_pipeline/
│   ├── logger.py         # Gravador de logs CSV
│   └── preprocessor.py   # Script de engenharia de atributos (resample 30s)
└── data/                 # Armazenamento dos datasets gerados
```
## ⚙️ Calibração de Hardware
O sistema foi otimizado para o seguinte setup:

Câmera: Logitech HD Pro C920 (1080p).

Monitor: 24 polegadas (1920x1080).

Parâmetros de Precisão: - amplitude_threshold: 2.9px (Sácadas).

horiz_margins: (0.43, 0.53) | vert_margins: (0.51, 0.61).

smoothing: 0.15 (EMA Filter).

📈 Updates Futuros (Roadmap)

[ ] Módulo de Machine Learning: Implementação de modelos classificadores (Random Forest / XGBoost) para predição de probabilidade de TDAH.

[ ] Data Visualization: Dashboard em Streamlit para visualização dos biomarcadores e mapas de calor de atenção.

[ ] Calibração Automática: Sistema de calibração dinâmica para diferentes tamanhos de tela e distâncias do usuário.

[ ] Deploy de Campo: Testes presenciais com voluntários.

👤 Autor
Tiago Rodrigues Plum Ferreira - Engenheiro de Computação (INATEL)
