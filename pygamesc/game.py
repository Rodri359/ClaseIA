import pygame
import random
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# Inicializar Pygame
pygame.init()

# Dimensiones de la pantalla
w, h = 800, 400
pantalla = pygame.display.set_mode((w, h))
pygame.display.set_caption("Juego: Disparo de Bala, Salto, Nave y Menú")

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)

# Variables globales
jugador = None
bala = None
fondo = None
nave = None
menu = None

# Variables de salto
salto = False
salto_altura = 15  # Velocidad inicial de salto
gravedad = 1
en_suelo = True

# Variables de pausa y menú
pausa = False
fuente = pygame.font.SysFont('Arial', 24)
menu_activo = True
modo_auto = False  # Indica si el modo de juego es automático
modo_modelo = None  # 'red_neuronal' o 'arbol' para decidir qué modelo usar

# Lista para guardar los datos de velocidad, distancia y salto (target)
datos_modelo = []
modelo_entrenado = None
modelo_entrenado_arbol = None

# Cargar las imágenes
jugador_frames = [
    pygame.image.load('pygamesc/assets/sprites/mono_frame_1.png'),
    pygame.image.load('pygamesc/assets/sprites/mono_frame_2.png'),
    pygame.image.load('pygamesc/assets/sprites/mono_frame_3.png'),
    pygame.image.load('pygamesc/assets/sprites/mono_frame_4.png')
]

bala_img = pygame.image.load('pygamesc/assets/sprites/purple_ball.png')
fondo_img = pygame.image.load('pygamesc/assets/game/fondo2.png')
nave_img = pygame.image.load('pygamesc/assets/game/ufo.png')
menu_img = pygame.image.load('pygamesc/assets/game/menu.png')

# Escalar la imagen de fondo
fondo_img = pygame.transform.scale(fondo_img, (w, h))

# Crear el rectángulo del jugador, bala y nave
jugador = pygame.Rect(50, h - 100, 32, 48)
bala = pygame.Rect(w - 50, h - 90, 16, 16)
nave = pygame.Rect(w - 100, h - 100, 64, 64)
menu_rect = pygame.Rect(w // 2 - 135, h // 2 - 90, 270, 180)

# Variables para la animación del jugador
current_frame = 0
frame_speed = 10
frame_count = 0

# Variables para la bala
velocidad_bala = -10
bala_disparada = False

# Variables para el fondo en movimiento
fondo_x1 = 0
fondo_x2 = w

def disparar_bala():
    global bala_disparada, velocidad_bala
    if not bala_disparada:
        velocidad_bala = random.randint(-8, -3)
        bala_disparada = True

def reset_bala():
    global bala, bala_disparada
    bala.x = w - 50
    bala_disparada = False

def manejar_salto():
    global jugador, salto, salto_altura, gravedad, en_suelo

    if salto:
        jugador.y -= salto_altura
        salto_altura -= gravedad
        # Cuando llega al suelo
        if jugador.y >= h - 100:
            jugador.y = h - 100
            salto = False
            salto_altura = 15
            en_suelo = True

def guardar_datos():
    global jugador, bala, velocidad_bala, salto
    distancia = abs(jugador.x - bala.x)
    salto_hecho = 1 if salto else 0
    datos_modelo.append((velocidad_bala, distancia, salto_hecho))

def generar_modelo(datos_modelo):
    global modelo_entrenado
    if len(datos_modelo) < 50:
        print("Se necesitan al menos 50 datos para entrenar el modelo.")
        return
    
    dataset = pd.DataFrame(datos_modelo, columns=['Feature 1', 'Feature 2', 'Label'])

    X = dataset.iloc[:, :2]  
    y = dataset.iloc[:, 2] 

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = Sequential([
        Dense(32, input_dim=2, activation='relu'),
        Dense(16, activation='relu'),
        Dense(8, activation='relu'),
        Dense(1, activation='sigmoid')
    ])

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    model.fit(X_train, y_train, epochs=200, batch_size=32, verbose=1)

    loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(f"\nPrecisión (RN) en el conjunto de prueba: {accuracy:.2f}")

    modelo_entrenado = model

def generar_arbol(datos_modelo):
    global modelo_entrenado_arbol 
    if len(datos_modelo) < 50:
        print("Se necesitan al menos 50 datos para entrenar el árbol de decisión.")
        return

    dataset = pd.DataFrame(datos_modelo, columns=['Feature 1', 'Feature 2', 'Label'])

    X = dataset.iloc[:, :2]  
    y = dataset.iloc[:, 2]  

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    clf = DecisionTreeClassifier()
    clf.fit(X_train, y_train)
    modelo_entrenado_arbol = clf

    plt.figure(figsize=(12, 8))
    plot_tree(
        clf,
        feature_names=['Feature 1', 'Feature 2'],
        class_names=['Clase 0', 'Clase 1'],
        filled=True,
        rounded=True
    )
    plt.title("Árbol de Decisión")
    plt.show()

    print("Árbol de decisión generado y mostrado con matplotlib.")

def pausa_juego():
    global pausa
    pausa = not pausa
    if pausa:
        print("Juego pausado. Datos registrados hasta ahora:", datos_modelo)
    else:
        print("Juego reanudado.")

def mostrar_menu():
    global menu_activo, modo_auto
    pantalla.fill(NEGRO)
    texto = fuente.render("Presiona 'M' para Manual, 'Q' para Salir", True, BLANCO)
    pantalla.blit(texto, (w // 4, h // 2))
    pygame.display.flip()

    while menu_activo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_m:
                    modo_auto = False
                    menu_activo = False
                elif evento.key == pygame.K_q:
                    print("Juego terminado. Datos recopilados:", datos_modelo)
                    pygame.quit()
                    exit()

def reiniciar_juego():
    global menu_activo, jugador, bala, nave, bala_disparada, salto, en_suelo
    menu_activo = True
    jugador.x, jugador.y = 50, h - 100
    bala.x = w - 50
    nave.x, nave.y = w - 100, h - 100
    bala_disparada = False
    salto = False
    en_suelo = True
    print("Datos recopilados para el modelo: ", datos_modelo)
    mostrar_menu()

def update():
    global bala, velocidad_bala, current_frame, frame_count, fondo_x1, fondo_x2

    fondo_x1 -= 1
    fondo_x2 -= 1

    if fondo_x1 <= -w:
        fondo_x1 = w
    if fondo_x2 <= -w:
        fondo_x2 = w

    pantalla.blit(fondo_img, (fondo_x1, 0))
    pantalla.blit(fondo_img, (fondo_x2, 0))

    frame_count += 1
    if frame_count >= frame_speed:
        current_frame = (current_frame + 1) % len(jugador_frames)
        frame_count = 0

    pantalla.blit(jugador_frames[current_frame], (jugador.x, jugador.y))
    pantalla.blit(nave_img, (nave.x, nave.y))

    if bala_disparada:
        bala.x += velocidad_bala

    if bala.x < 0:
        reset_bala()

    pantalla.blit(bala_img, (bala.x, bala.y))

    if jugador.colliderect(bala):
        print("Colisión detectada!")
        reiniciar_juego()

def main():
    global salto, en_suelo, bala_disparada, modo_auto, modo_modelo

    reloj = pygame.time.Clock()
    mostrar_menu()  
    correr = True

    while correr:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                correr = False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE and en_suelo and not pausa and not modo_auto:
                    salto = True
                    en_suelo = False
                if evento.key == pygame.K_p:
                    pausa_juego()
                if evento.key == pygame.K_q:
                    print("Juego terminado. Datos recopilados:", datos_modelo)
                    pygame.quit()
                    exit()
                if evento.key == pygame.K_m:
                    modo_modelo = None
                    modo_auto = False
                if evento.key == pygame.K_t and not modo_auto:
                    # Entrenar ambos modelos
                    generar_modelo(datos_modelo)
                    generar_arbol(datos_modelo)
                    mostrar_menu()
                    print("Modelos entrenados. Presiona 'A' para usar RN o 'e' para usar Árbol en modo automático.")
                if evento.key == pygame.K_a:  # Modo automático con RN
                    if modelo_entrenado is not None:
                        modo_auto = True
                        modo_modelo = 'red_neuronal'
                        print("Modo automático activado (Red Neuronal).")
                    else:
                        print("Primero entrena el modelo con 't'.")

                if evento.key == pygame.K_e:  # Modo automático con Árbol
                    if modelo_entrenado_arbol is not None:
                        modo_auto = True
                        modo_modelo = 'arbol'
                        print("Modo automático activado (Árbol de Decisión).")
                    else:
                        print("Primero entrena el modelo con 't'.")

        if not pausa:
            if modo_auto:
                # Modo automático según el modelo seleccionado
                distancia = abs(jugador.x - bala.x)
                X_pred = np.array([[velocidad_bala, distancia]])

                # Predicción según el modelo actual
                if modo_modelo == 'red_neuronal' and modelo_entrenado is not None:
                    prediccion = modelo_entrenado.predict(X_pred)
                    if prediccion[0][0] > 0.5 and en_suelo:
                        salto = True
                        en_suelo = False
                elif modo_modelo == 'arbol' and modelo_entrenado_arbol is not None:
                    prediccion = modelo_entrenado_arbol.predict(X_pred)
                    if prediccion[0] == 1 and en_suelo:
                        salto = True
                        en_suelo = False

                if salto:
                    manejar_salto()
            else:
                # Modo manual
                if salto:
                    manejar_salto()
                guardar_datos()

            if not bala_disparada:
                disparar_bala()
            update()

        pygame.display.flip()
        reloj.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
