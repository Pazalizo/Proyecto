import pygame
import random

# Configuración inicial de Pygame
pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulación de Gasolinera")
clock = pygame.time.Clock()

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (144, 238, 144)  # Gasolina
RED = (255, 182, 193)  # Diésel
ORANGE = (255, 165, 0)  # Dispensadores
GRAY = (200, 200, 200)  # Filas

# Posiciones de los tanques de combustible
TANQUE_GASOLINA_POS = (150, 600)
TANQUE_DIESEL_POS = (850, 600)

# Posiciones de los dispensadores
DISPENSADORES_POS = [
    (300, 300),  # Dispensador 1
    (500, 300),  # Dispensador 2
    (700, 300),  # Dispensador 3
]

# Configuración de filas, encima de cada dispensador
filas = [
    {"tipo": "Gasolina", "pos": (270, 250), "vehiculos": []},
    {"tipo": "Gasolina", "pos": (330, 250), "vehiculos": []},
    {"tipo": "Diésel", "pos": (390, 250), "vehiculos": []},
    
    {"tipo": "Gasolina", "pos": (470, 250), "vehiculos": []},
    {"tipo": "Gasolina", "pos": (530, 250), "vehiculos": []},
    {"tipo": "Diésel", "pos": (590, 250), "vehiculos": []},
    
    {"tipo": "Diésel", "pos": (670, 250), "vehiculos": []},
    {"tipo": "Diésel", "pos": (730, 250), "vehiculos": []},
]

# Clase para el vehículo
class Vehiculo:
    def __init__(self, tipo):
        self.tipo = tipo
        self.color = GREEN if tipo == "Gasolina" else RED
        self.rect = pygame.Rect(random.randint(50, 100), random.randint(400, 500), 20, 40)
        self.speed = 2
        self.target_lane = None
        self.atendido = False

    def seleccionar_fila(self, filas):
        # Filtra las filas según el tipo de combustible
        filas_tipo = [fila for fila in filas if fila["tipo"] == self.tipo]
        # Selecciona una fila aleatoria de las filas disponibles para su tipo de combustible
        self.target_lane = random.choice(filas_tipo)

    def mover_a_fila(self):
        # Mueve el vehículo hacia su fila objetivo
        if self.target_lane:
            destino_x, destino_y = self.target_lane["pos"]
            # Coloca el vehículo detrás del último en la fila, sin superposición
            if len(self.target_lane["vehiculos"]) > 0:
                ultimo_vehiculo = self.target_lane["vehiculos"][-1]
                destino_y = ultimo_vehiculo.rect.y - 50  # Mantiene 50 px de distancia

            if self.rect.x < destino_x:
                self.rect.x += self.speed
            elif self.rect.x > destino_x:
                self.rect.x -= self.speed

            if self.rect.y < destino_y:
                self.rect.y += self.speed
            elif self.rect.y > destino_y:
                self.rect.y -= self.speed
            else:
                # Agrega el vehículo a la fila una vez que llega a la posición correcta
                self.target_lane["vehiculos"].append(self)
                self.atendido = True

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color, self.rect)

# Lista de vehículos
vehiculos = []

# Bucle principal de simulación
running = True
while running:
    screen.fill(WHITE)

    # Eventos de Pygame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Generación aleatoria de vehículos
    if random.randint(0, 100) < 2:  # Ajusta la probabilidad según desees
        tipo = "Gasolina" if random.random() < 0.7 else "Diésel"
        vehiculo = Vehiculo(tipo)
        vehiculo.seleccionar_fila(filas)
        vehiculos.append(vehiculo)

    # Dibujar filas
    for fila in filas:
        pygame.draw.rect(screen, GRAY, (*fila["pos"], 40, 60))
        for vehiculo in fila["vehiculos"]:
            vehiculo.dibujar(screen)

    # Mover y dibujar vehículos
    for vehiculo in vehiculos:
        if not vehiculo.atendido:
            vehiculo.mover_a_fila()
        vehiculo.dibujar(screen)

    # Dibujar dispensadores
    for dispensador in DISPENSADORES_POS:
        color = GREEN if DISPENSADORES_POS.index(dispensador) < 2 else RED
        pygame.draw.ellipse(screen, ORANGE, (*dispensador, 100, 50))  # Dispensador ovalado

    # Dibujar tanques subterráneos
    pygame.draw.circle(screen, GREEN, TANQUE_GASOLINA_POS, 30)
    pygame.draw.circle(screen, RED, TANQUE_DIESEL_POS, 30)

    # Actualizar pantalla
    pygame.display.flip()
    clock.tick(30)  # Velocidad de fotogramas

pygame.quit()
