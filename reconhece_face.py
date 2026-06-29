import face_recognition
import cv2
import pickle

# Carregar o rosto cadastrado
with open("meu_rosto.pkl", "rb") as file:
    my_face_encoding = pickle.load(file)

# Inicializar a câmera
video_capture = cv2.VideoCapture(0)

print("Sistema de Reconhecimento Ativado. Pressione 'q' para sair.")

while True:
    ret, frame = video_capture.read()

    # Encontrar faces no frame capturado
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    
    for face_encoding, face_location in zip(face_encodings, face_locations):
        # Comparar o rosto atual com o rosto cadastrado
        matches = face_recognition.compare_faces([my_face_encoding], face_encoding, tolerance=0.6)
        top, right, bottom, left = face_location

        if matches[0]:
            label = "Reconhecido: Voce"
            color = (0, 255, 0)  # Verde
        else:
            label = "Não Reconhecido"
            color = (0, 0, 255)  # Vermelho

        # Desenhar o retângulo ao redor da face e exibir a mensagem
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    cv2.imshow("Reconhecimento Facial", frame)
    
    # Pressionar 'q' para sair
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
