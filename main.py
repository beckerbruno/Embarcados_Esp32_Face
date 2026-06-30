import sys
import cv2
import face_recognition
import pickle
import os
import serial
import time
from PyQt5.QtCore import QTimer
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QInputDialog, QMessageBox
from PyQt5 import uic

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_CADASTROS = os.path.join(BASE_DIR, "cadastros")
os.makedirs(PASTA_CADASTROS, exist_ok=True)

PORTA_SERIAL = 'COM3' 
BAUD_RATE = 115200

try:
    esp_serial = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=1)
except Exception as e:
    print(f"Aviso: Não foi possível conectar ao ESP na porta {PORTA_SERIAL}. Erro: {e}")
    esp_serial = None

class PortariaApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("interface.ui", self) 
        
        # Variáveis de controle
        self.capture = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.atualizar_frame)
        
        self.rostos_conhecidos = []
        self.nomes_conhecidos = []
        self.carregar_cadastros()
        
        self.ultimo_acionamento = 0
        self.tempo_cooldown = 4.0 

        # --- Variáveis de Otimização ---
        self.contador_frames = 0
        self.processar_a_cada = 3  # Processa o reconhecimento a cada 3 frames
        self.escala_processamento = 0.45
        self.resultados_exibicao = [] # Guarda o último resultado para não piscar a tela

        # Conecta os botões
        self.Btn_Iniciar.clicked.connect(self.iniciar_camera)
        self.Btn_Parar.clicked.connect(self.parar_camera)
        self.Btn_Cadastrar.clicked.connect(self.cadastrar_rosto)

    def carregar_cadastros(self):
        self.rostos_conhecidos.clear()
        self.nomes_conhecidos.clear()
        for arquivo in os.listdir(PASTA_CADASTROS):
            if arquivo.endswith(".pkl"):
                caminho = os.path.join(PASTA_CADASTROS, arquivo)
                with open(caminho, "rb") as f:
                    self.rostos_conhecidos.append(pickle.load(f))
                self.nomes_conhecidos.append(os.path.splitext(arquivo)[0])

    def iniciar_camera(self):
        if self.capture is None:
            self.capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            
            # --- OTIMIZAÇÃO: Diminuir resolução de entrada e buffer da câmera ---
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1) # Reduz atraso acumulado
            
            self.timer.start(30) # Aumentei a taxa de atualização da interface para 30ms para ficar mais fluido
            self.LblStatus.setText("Monitoramento Ativo")
            self.LblStatus.setStyleSheet("color: blue;")

    def parar_camera(self):
        self.timer.stop()
        if self.capture:
            self.capture.release()
            self.capture = None
        self.AreaCamera.clear()
        self.LblStatus.setText("Sistema Inativo")
        self.LblStatus.setStyleSheet("color: black;")
        self.resultados_exibicao.clear() # Limpa o cache de retângulos

    def enviar_comando_esp(self, reconhecido, nome=""):
        agora = time.time()
        if agora - self.ultimo_acionamento > self.tempo_cooldown:
            if reconhecido:
                self.LblStatus.setText(f"Acesso Liberado: {nome}")
                self.LblStatus.setStyleSheet("color: green;")
                if esp_serial: esp_serial.write(b'1')
            else:
                self.LblStatus.setText("Acesso Negado")
                self.LblStatus.setStyleSheet("color: red;")
                if esp_serial: esp_serial.write(b'0')
            
            self.ultimo_acionamento = agora

    def atualizar_frame(self):
        ret, frame = self.capture.read()
        if not ret: return

        self.contador_frames += 1

        # --- OTIMIZAÇÃO: Só roda o face_recognition a cada X frames ---
        if self.contador_frames % self.processar_a_cada == 0:
            
            frame_pequeno = cv2.resize(frame, (0, 0), fx=self.escala_processamento, fy=self.escala_processamento)
            frame_rgb = cv2.cvtColor(frame_pequeno, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(frame_rgb, model="hog")
            face_encodings = face_recognition.face_encodings(frame_rgb, face_locations)

            reconheceu_alguem = False
            novos_resultados = [] # Prepara uma nova lista de caixas para desenhar

            for face_encoding, face_location in zip(face_encodings, face_locations):
                cor = (0, 0, 255) # Vermelho padrão
                
                if self.rostos_conhecidos:
                    distancias = face_recognition.face_distance(self.rostos_conhecidos, face_encoding)
                    if len(distancias) > 0:
                        indice = distancias.argmin()

                        if distancias[indice] <= 0.6:
                            nome_encontrado = self.nomes_conhecidos[indice]
                            cor = (0, 255, 0) # Verde
                            reconheceu_alguem = True
                            self.enviar_comando_esp(True, nome_encontrado)

                # Escalar de volta para o tamanho original do frame
                escala = int(1 / self.escala_processamento)
                top, right, bottom, left = [coord * escala for coord in face_location]
                
                # Salva o resultado no cache
                novos_resultados.append(((left, top, right, bottom), cor))
                
            # Atualiza o cache da tela com as detecções do frame atual
            self.resultados_exibicao = novos_resultados
            
            if not reconheceu_alguem and len(face_locations) > 0:
                 self.enviar_comando_esp(False)

        # --- DESENHA OS RETÂNGULOS (Usando os dados em cache nos frames pulados) ---
        for (left, top, right, bottom), cor in self.resultados_exibicao:
            cv2.rectangle(frame, (left, top), (right, bottom), cor, 2)

        # Converter e exibir na UI
        image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888).rgbSwapped()
        self.AreaCamera.setPixmap(QPixmap.fromImage(image))

    def cadastrar_rosto(self):
        if self.capture is None:
            QMessageBox.warning(self, "Aviso", "Ligue a câmera primeiro!")
            return

        ret, frame = self.capture.read()
        if ret:
            face_locations = face_recognition.face_locations(frame)
            if len(face_locations) == 0:
                QMessageBox.warning(self, "Aviso", "Nenhum rosto detectado para cadastro.")
                return

            face_encodings = face_recognition.face_encodings(frame, face_locations)
            
            nome, ok = QInputDialog.getText(self, 'Cadastro', 'Digite o nome do usuário:')
            if ok and nome:
                caminho_arquivo = os.path.join(PASTA_CADASTROS, f"{nome.strip()}.pkl")
                with open(caminho_arquivo, "wb") as arquivo:
                    pickle.dump(face_encodings[0], arquivo)
                
                QMessageBox.information(self, "Sucesso", "Cadastro realizado!")
                self.carregar_cadastros() 

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = PortariaApp()
    window.show()
    sys.exit(app.exec_())