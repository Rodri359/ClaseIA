import cv2 as cv
import numpy as np

# Ruta del video
video_path = 'C:/Users/rodri/Videos/Grabaciones de pantalla/18.mp4'  # Asegúrate de que sea un archivo de video válido
cap = cv.VideoCapture(video_path)

lower = np.array([0, 0, 0])  # Límite inferior
upper = np.array([150, 150, 150])  # Límite superiorq
i = 0

if not cap.isOpened():
    print("Error: No se pudo abrir el archivo de video. Verifica la ruta o el formato.")
    exit()

while True:
    # Leer cada frame del video
    ret, frame = cap.read()
    if not ret:
        print("No hay más frames o hubo un problema leyendo el video.")
        break

    # Convertir de BGR a HSV
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    # Crear la máscara para el color con rango
    mask = cv.inRange(hsv, lower, upper)

    # Aplicar operaciones morfológicas para limpiar la máscara
    mask = cv.erode(mask, None, iterations=2)
    mask = cv.dilate(mask, None, iterations=2)

    # Encontrar contornos en la máscara
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    # Procesar los contornos detectados
    if contours:
        # Obtener el contorno más grande
        largest_contour = max(contours, key=cv.contourArea)

        # Encontrar el centro del contorno usando un círculo mínimo que lo rodee
        ((x, y), radius) = cv.minEnclosingCircle(largest_contour)

        # Verificar que el radio sea válido
        if radius > 10:
            x_start = max(0, int(x - radius))
            y_start = max(0, int(y - radius))
            x_end = min(frame.shape[1], int(x + radius))
            y_end = min(frame.shape[0], int(y + radius))

            # Recortar la región de interés (ROI)
            img2 = frame[y_start:y_end, x_start:x_end]
            if img2.size > 0:
                img2 = cv.resize(img2, (50, 50), interpolation=cv.INTER_AREA)
                cv.imwrite(f'C:/Users/rodri/Downloads/TareasIA/dataset/bugatti/18_{i}.jpg', img2)
                i += 1

                # Mostrar la región de interés
                cv.imshow('ROI', img2)

    # Mostrar el frame original y la máscara
    cv.imshow('Frame', frame)
    cv.imshow('Mask', mask)

    # Salir al presionar 'q'
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar el video y cerrar las ventanas
cap.release()
cv.destroyAllWindows()
