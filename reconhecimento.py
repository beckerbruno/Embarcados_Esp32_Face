import cv2
import face_recognition
import pickle
import os


rostos_conhecidos = []
nomes_conhecidos = []

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_CADASTROS = os.path.join(BASE_DIR, "cadastros")

# Ajustes de desempenho. Se ainda pesar, aumente PROCESSAR_A_CADA para 4 ou 5.
ESCALA_PROCESSAMENTO = 0.45
PROCESSAR_A_CADA = 5
TOLERANCIA = 0.6

for arquivo in os.listdir(PASTA_CADASTROS):

    if arquivo.endswith(".pkl"):

        caminho = os.path.join(PASTA_CADASTROS, arquivo)

        with open(caminho, "rb") as f:
            encoding = pickle.load(f)

        rostos_conhecidos.append(encoding)

        nomes_conhecidos.append(
            os.path.splitext(arquivo)[0]
        )

print(f"{len(nomes_conhecidos)} rostos carregados.")


video_capture = cv2.VideoCapture(0)
video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
video_capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

print("Sistema ativado.")
print("Pressione Q para sair.")

contador_frames = 0
resultados_exibicao = []

while True:

    ret, frame = video_capture.read()

    if not ret:
        print("Erro ao acessar câmera.")
        break

    if contador_frames % PROCESSAR_A_CADA == 0:

        frame_pequeno = cv2.resize(
            frame,
            (0, 0),
            fx=ESCALA_PROCESSAMENTO,
            fy=ESCALA_PROCESSAMENTO
        )
        frame_rgb = cv2.cvtColor(frame_pequeno, cv2.COLOR_BGR2RGB)

        # Detectar em imagem menor deixa o reconhecimento bem mais leve.
        face_locations = face_recognition.face_locations(
            frame_rgb,
            model="hog"
        )

        face_encodings = face_recognition.face_encodings(
            frame_rgb,
            face_locations
        )

        resultados_exibicao = []

        for face_encoding, face_location in zip(face_encodings, face_locations):

            texto = "ACESSO NEGADO"
            cor = (0, 0, 255)

            if rostos_conhecidos:

                distancias = face_recognition.face_distance(
                    rostos_conhecidos,
                    face_encoding
                )
                indice = distancias.argmin()

                if distancias[indice] <= TOLERANCIA:
                    nome_encontrado = nomes_conhecidos[indice]
                    texto = f"LIBERADO: {nome_encontrado}"
                    cor = (0, 255, 0)

            top, right, bottom, left = face_location
            escala = int(1 / ESCALA_PROCESSAMENTO)
            face_location_original = (
                top * escala,
                right * escala,
                bottom * escala,
                left * escala
            )
            resultados_exibicao.append((face_location_original, texto, cor))

    contador_frames += 1

    for face_location, texto, cor in resultados_exibicao:

        top, right, bottom, left = face_location

        # Retângulo
        cv2.rectangle(
            frame,
            (left, top),
            (right, bottom),
            cor,
            2
        )

        # Texto
        cv2.putText(
            frame,
            texto,
            (left, top - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            cor,
            2
        )

    cv2.imshow(
        "Reconhecimento Facial",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
