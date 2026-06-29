import face_recognition
import cv2
import pickle

# Inicializar a câmera
video_capture = cv2.VideoCapture(0)

print("Posicione-se na frente da câmera. Pressione 'c' para capturar seu rosto.")

while True:
    ret, frame = video_capture.read()
    cv2.imshow("Cadastro - Pressione 'c' para capturar", frame)
        
    # Pressionar 'c' para capturar a imagem
    if cv2.waitKey(1) & 0xFF == ord('c'):

        face_locations = face_recognition.face_locations(frame)
        if len(face_locations) > 0:
            # Capturar as características do rosto
            face_encodings = face_recognition.face_encodings(frame, face_locations)
            with open("meu_rosto.pkl", "wb") as file:
                pickle.dump(face_encodings[0], file)  # Salva apenas o primeiro rosto encontrado
            print("Cadastro realizado com sucesso!")
            break
        else:
            print("Nenhum rosto encontrado. Tente novamente.")

video_capture.release()
cv2.destroyAllWindows()