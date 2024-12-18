import pygame
from queue import PriorityQueue

# Configuraciones iniciales
ANCHO_VENTANA = 600
VENTANA = pygame.display.set_mode((ANCHO_VENTANA, ANCHO_VENTANA))
pygame.display.set_caption("Visualización de Nodos")

# Colores (RGB)
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
GRIS = (128, 128, 128)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
NARANJA = (255, 165, 0)
PURPURA = (128, 0, 128)
AZUL = (0, 0, 255)
# Nuevo color para la lista cerrada
CERRADO = (192, 192, 192)

class Nodo:
    def __init__(self, fila, col, ancho, total_filas):
        self.fila = fila
        self.col = col
        self.x = fila * ancho
        self.y = col * ancho
        self.color = BLANCO
        self.ancho = ancho
        self.total_filas = total_filas
        self.vecinos = []

    def get_pos(self):
        return self.fila, self.col

    def es_pared(self):
        return self.color == NEGRO

    def es_inicio(self):
        return self.color == NARANJA

    def es_fin(self):
        return self.color == PURPURA

    def restablecer(self):
        self.color = BLANCO

    def hacer_inicio(self):
        self.color = NARANJA

    def hacer_pared(self):
        self.color = NEGRO

    def hacer_fin(self):
        self.color = PURPURA

    def hacer_camino(self):
        self.color = AZUL

    def hacer_corto(self):
        self.color = PURPURA

    def hacer_cerrado(self):
        self.color = CERRADO

    def agregar_vecinos(self, grid):
        self.vecinos = []
        if self.fila < self.total_filas - 1 and not grid[self.fila + 1][self.col].es_pared():  # Abajo
            self.vecinos.append(grid[self.fila + 1][self.col])
        if self.fila > 0 and not grid[self.fila - 1][self.col].es_pared():  # Arriba
            self.vecinos.append(grid[self.fila - 1][self.col])
        if self.col < self.total_filas - 1 and not grid[self.fila][self.col + 1].es_pared():  # Derecha
            self.vecinos.append(grid[self.fila][self.col + 1])
        if self.col > 0 and not grid[self.fila][self.col - 1].es_pared():  # Izquierda
            self.vecinos.append(grid[self.fila][self.col - 1])

         # Diagonales
        if self.fila < self.total_filas - 1 and self.col < self.total_filas - 1 and not grid[self.fila + 1][self.col + 1].es_pared():  # Abajo-Derecha
            self.vecinos.append(grid[self.fila + 1][self.col + 1])
        if self.fila < self.total_filas - 1 and self.col > 0 and not grid[self.fila + 1][self.col - 1].es_pared():  # Abajo-Izquierda
            self.vecinos.append(grid[self.fila + 1][self.col - 1])
        if self.fila > 0 and self.col < self.total_filas - 1 and not grid[self.fila - 1][self.col + 1].es_pared():  # Arriba-Derecha
            self.vecinos.append(grid[self.fila - 1][self.col + 1])
        if self.fila > 0 and self.col > 0 and not grid[self.fila - 1][self.col - 1].es_pared():  # Arriba-Izquierda
            self.vecinos.append(grid[self.fila - 1][self.col - 1])

    def dibujar(self, ventana):
        pygame.draw.rect(ventana, self.color, (self.x, self.y, self.ancho, self.ancho))
    
    
    def __repr__(self):
        return f"Nodo({self.fila}, {self.col})"

def heuristica(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)
    return dx + dy + (1.4 - 2) * min(dx, dy)  # Penalización para movimientos diagonales

def reconstruir_camino(padre, nodo_actual, dibujar):
    while nodo_actual in padre:
        nodo_actual = padre[nodo_actual]
        nodo_actual.hacer_corto()  
        dibujar()

def a_estrella(grid, inicio, fin, dibujar):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, inicio))
    padre = {}
    g_score = {nodo: float("inf") for fila in grid for nodo in fila}
    g_score[inicio] = 0
    f_score = {nodo: float("inf") for fila in grid for nodo in fila}
    f_score[inicio] = heuristica(inicio.get_pos(), fin.get_pos())

    open_set_hash = {inicio}
    closed_set = set()

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        _, _, nodo_actual = open_set.get()
        open_set_hash.remove(nodo_actual)

        if nodo_actual in closed_set:
            continue

        closed_set.add(nodo_actual)

        if nodo_actual == fin:
            reconstruir_camino(padre, fin, dibujar)
            print("Lista cerrada:", [n.get_pos() for n in closed_set])
            return True

        if nodo_actual != inicio and nodo_actual != fin:
            nodo_actual.hacer_cerrado()

        for vecino in nodo_actual.vecinos:
            if vecino in closed_set:
                continue

            # Ajuste del costo para movimientos diagonales
            if abs(nodo_actual.fila - vecino.fila) == 1 and abs(nodo_actual.col - vecino.col) == 1:
                temp_g_score = g_score[nodo_actual] + 1.4
            else:
                temp_g_score = g_score[nodo_actual] + 1

            if temp_g_score < g_score[vecino]:
                padre[vecino] = nodo_actual
                g_score[vecino] = temp_g_score
                f_score[vecino] = temp_g_score + heuristica(vecino.get_pos(), fin.get_pos())

                if vecino not in open_set_hash:
                    count += 1
                    # Factor de desempate: sumamos una pequeña fracción dependiente de la heurística
                    prioridad = f_score[vecino] + 0.001 * heuristica(vecino.get_pos(), fin.get_pos())
                    open_set.put((prioridad, count, vecino))
                    open_set_hash.add(vecino)

        dibujar()

    print("No se encontró un camino.")
    return False


def crear_grid(filas, ancho):
    grid = []
    ancho_nodo = ancho // filas
    for i in range(filas):
        grid.append([])
        for j in range(filas):
            nodo = Nodo(i, j, ancho_nodo, filas)
            grid[i].append(nodo)
    return grid

def dibujar_grid(ventana, filas, ancho):
    ancho_nodo = ancho // filas
    for i in range(filas):
        pygame.draw.line(ventana, GRIS, (0, i * ancho_nodo), (ancho, i * ancho_nodo))
        for j in range(filas):
            pygame.draw.line(ventana, GRIS, (j * ancho_nodo, 0), (j * ancho_nodo, ancho))

def dibujar(ventana, grid, filas, ancho):
    ventana.fill(BLANCO)
    for fila in grid:
        for nodo in fila:
            nodo.dibujar(ventana)

    dibujar_grid(ventana, filas, ancho)
    pygame.display.update()

def obtener_click_pos(pos, filas, ancho):
    ancho_nodo = ancho // filas
    y, x = pos
    fila = y // ancho_nodo
    col = x // ancho_nodo
    return fila, col

def main(ventana, ancho):
    FILAS = 5
    grid = crear_grid(FILAS, ancho)

    inicio = None
    fin = None

    corriendo = True

    while corriendo:
        dibujar(ventana, grid, FILAS, ancho)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                corriendo = False

            if pygame.mouse.get_pressed()[0]:  # Click izquierdo
                pos = pygame.mouse.get_pos()
                fila, col = obtener_click_pos(pos, FILAS, ancho)
                if fila >= FILAS or col >= FILAS:
                    continue  # Evitar errores si el clic está fuera de la cuadrícula
                nodo = grid[fila][col]
                if not inicio and nodo != fin:
                    inicio = nodo
                    inicio.hacer_inicio()

                elif not fin and nodo != inicio:
                    fin = nodo
                    fin.hacer_fin()

                elif nodo != fin and nodo != inicio:
                    nodo.hacer_pared()

            elif pygame.mouse.get_pressed()[2]:  # Click derecho
                pos = pygame.mouse.get_pos()
                fila, col = obtener_click_pos(pos, FILAS, ancho)
                if fila >= FILAS or col >= FILAS:
                    continue  # Evitar errores si el clic está fuera de la cuadrícula
                nodo = grid[fila][col]
                nodo.restablecer()
                if nodo == inicio:
                    inicio = None
                elif nodo == fin:
                    fin = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and inicio and fin:
                    for fila in grid:
                        for nodo in fila:
                            nodo.agregar_vecinos(grid)

                    a_estrella(grid, inicio, fin, lambda: dibujar(ventana, grid, FILAS, ancho))

                if event.key == pygame.K_r:  # Reiniciar el tablero completo
                    inicio = None
                    fin = None
                    grid = crear_grid(FILAS, ancho)

    pygame.quit()

main(VENTANA, ANCHO_VENTANA)
