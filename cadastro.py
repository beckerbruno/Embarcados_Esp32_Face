import cv2
import face_recognition
import pickle
import os

# Criar pasta de cadastros se não existir
os.makedirs("cadastros", exist_ok=True)

# Inicializar câmera
video_capture = cv2.VideoCapture(0)

print("Posicione-se na frente da câmera.")
print("Pressione C para cadastrar.")
print("Pressione Q para sair.")

while True:

    ret, frame = video_capture.read()

    if not ret:
        print("Erro ao acessar câmera")
        break

    cv2.imshow("Cadastro Facial", frame)

    tecla = cv2.waitKey(1) & 0xFF

    # Sair
    if tecla == ord('q'):
        break

    # Cadastrar
    if tecla == ord('c'):

        print("Capturando rosto...")

        face_locations = face_recognition.face_locations(frame)

        if len(face_locations) == 0:
            print("Nenhum rosto encontrado.")
            continue

        face_encodings = face_recognition.face_encodings(
            frame,
            face_locations
        )

        nome = input("Digite o nome da pessoa: ").strip()

        caminho_arquivo = f"cadastros/{nome}.pkl"

        with open(caminho_arquivo, "wb") as arquivo:
            pickle.dump(face_encodings[0], arquivo)

        print(f"Cadastro realizado com sucesso!")
        print(f"Arquivo salvo em: {caminho_arquivo}")

        break

video_capture.release()
cv2.destroyAllWindows()