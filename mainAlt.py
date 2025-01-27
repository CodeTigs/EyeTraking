import asyncio
import websockets
import json
import subprocess
import os
import time
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import cv2
import tkinter as tk
from tkinter import Button, filedialog, Label
import threading
import time
DATA_DIR = 'data'
FILENAME = 'gaze_data.json'
OUTPUT_DIR = 'images'
OUTPUT_FILENAME = 'heatmap.png'

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

ConnectionAuthorizationStatus = None

selected_image_path = None
selected_video_path2 = None
selected_video_path3 = None

async def start_capture():
    shortcut_path = 'C:\\Users\\Public\\Desktop\\GazePointer.lnk' 
    try:
        print(f"Executando {shortcut_path}...")
        subprocess.run(['cmd', '/c', 'start','/min', '', shortcut_path], check=True)
        print(f"{shortcut_path} executado com sucesso!")
        time.sleep(6)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar {shortcut_path}: {e}")
        return
    time.sleep(6)
    await connect()

def finalize_processing():
    """
    Finaliza a conexão WebSocket, mata o processo e gera o heatmap.
    """
    # Cancelar a conexão WebSocket
    global ConnectionAuthorizationStatus
    if ConnectionAuthorizationStatus is not None:
        ConnectionAuthorizationStatus = None
        print("Conexão WebSocket encerrada.")

    # Matar o processo do GazePointer
    process_name = "GazePointer.exe"
    kill_process_by_name(process_name)

    # Gerar o heatmap
    try:
        generate_heatmap()
        print("Mapa de calor gerado com sucesso.")
    except Exception as e:
        print(f"Erro ao gerar o mapa de calor: {e}")


def start_process():
    # Inicia a captura de dados oculares
    threading.Thread(target=asyncio.run, args=(start_capture(),)).start()
    return "Captura iniciada!"

def kill_process_by_name(process_name):
    try:
        subprocess.run(['taskkill', '/f', '/im', process_name], check=True)
        print(f"Processo {process_name} encerrado com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao encerrar o processo {process_name}: {e}")

def generate_heatmap():
    filepath = os.path.join(DATA_DIR, FILENAME)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"O arquivo {filepath} não foi encontrado.")
    with open(filepath, 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    if 'GazeX' not in df.columns or 'GazeY' not in df.columns:
        raise ValueError("As colunas 'GazeX' e 'GazeY' são necessárias para gerar o mapa de calor.")
    plt.figure(figsize=(10, 8))
    sns.kdeplot(x=df['GazeX'], y=df['GazeY'], cmap="Blues", fill=True, thresh=0.05)
    plt.title('Mapa de Calor dos Dados de Gaze')
    plt.xlabel('GazeX')
    plt.ylabel('GazeY')
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
    plt.savefig(output_path)
    plt.show()

async def connect(app_key="AppKeyTrial", port=43333):
    url = f"ws://127.0.0.1:{port}"
    try:
        async with websockets.connect(url) as websocket:
            print("Conexão WebSocket estabelecida.")
            await websocket.send(app_key)
            print(f"AppKey enviada: {app_key}")
            global ConnectionAuthorizationStatus
            while True:
                received_msg = await websocket.recv()
                if ConnectionAuthorizationStatus is None:
                    ConnectionAuthorizationStatus = received_msg
                    if not ConnectionAuthorizationStatus.startswith("ok"):
                        print(f"Status da conexão: {ConnectionAuthorizationStatus}")
                        break
                else:
                    gaze_data = json.loads(received_msg)
                    plot_gaze_data(gaze_data)
    except (websockets.exceptions.ConnectionClosedError, ConnectionRefusedError):
        print("Não foi possível conectar ao servidor. Certifique-se de que o GazePointer está em execução.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

def plot_gaze_data(gaze_data):
    try:
        timestamp = time.time()
        gaze_data['timestamp'] = timestamp
        filepath = os.path.join(DATA_DIR, FILENAME)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                existing_data = json.load(f)
        else:
            existing_data = []
        existing_data.append(gaze_data)
        with open(filepath, 'w') as f:
            json.dump(existing_data, f, indent=4)
        print(f"Dados do Gaze recebidos: {gaze_data}")
    except Exception as e:
        print(f"Erro ao salvar os dados: {e}")

def play_videos():
    if not selected_image_path or not selected_video_path2:
        print("Selecione uma imagem e o vídeo 2 antes de iniciar.")
        return

    # Iniciar o processamento antes de reproduzir os vídeos
    start_process()
    time.sleep(12)
    image = cv2.imread(selected_image_path)
    cap2 = cv2.VideoCapture(selected_video_path2)
    while True:
        ret2, frame2 = cap2.read()
        if not ret2:
            break
        frame1 = cv2.resize(image, (640, 360))
        frame2 = cv2.resize(frame2, (640, 360))
        combined_frame = cv2.hconcat([frame1, frame2])
        cv2.namedWindow('Videos Simultaneos', cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty('Videos Simultaneos', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow('Videos Simultaneos', combined_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap2.release()
    cv2.destroyAllWindows()

    # Finalizar conexão e gerar heatmap ao término
    finalize_processing()


def play_video3():
    if not selected_video_path3:
        print("Selecione o vídeo 3 antes de iniciar.")
        return

    # Iniciar o processamento antes de reproduzir o vídeo
    start_process()
    time.sleep(8)
    cap3 = cv2.VideoCapture(selected_video_path3)
    while True:
        ret3, frame3 = cap3.read()
        if not ret3:
            break
        cv2.namedWindow('Video Final', cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty('Video Final', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow('Video Final', frame3)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap3.release()
    cv2.destroyAllWindows()

    # Finalizar conexão e gerar heatmap ao término
    finalize_processing()


def create_gui():
    global selected_image_path, selected_video_path2, selected_video_path3

    root = tk.Tk()
    root.title('Controle de Vídeos')

    def select_image_and_video_2():
        global selected_image_path, selected_video_path2
        selected_image_path = filedialog.askopenfilename(title="Selecione a Imagem Estática")
        selected_video_path2 = filedialog.askopenfilename(title="Selecione o Vídeo 2")
        print(f"Imagem selecionada: {selected_image_path}")
        print(f"Vídeo 2 selecionado: {selected_video_path2}")

    def select_video_3():
        global selected_video_path3
        selected_video_path3 = filedialog.askopenfilename(title="Selecione o Vídeo 3")
        print(f"Vídeo 3 selecionado: {selected_video_path3}")

    Button(root, text='Selecionar Imagem e Vídeo 2', command=select_image_and_video_2).pack(pady=10)
    Button(root, text='Selecionar Vídeo 3', command=select_video_3).pack(pady=10)
    Button(root, text='Iniciar Imagem e Vídeo 2', command=play_videos).pack(pady=10)
    Button(root, text='Iniciar Vídeo 3', command=play_video3).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
