import simpy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Parámetros de la simulación
TIEMPO_LLENADO_MIN = 20  # en segundos
TIEMPO_LLENADO_MAX = 100
CAPACIDAD_TANQUE_GASOLINA = 12000  # en galones
CAPACIDAD_TANQUE_DIESEL = 12000
UMBRAL_PEDIDO = 200  # Umbral para solicitar reabastecimiento
TIEMPO_REABASTECIMIENTO_MIN = 1800  # Tiempo en segundos (media hora)
TIEMPO_REABASTECIMIENTO_MAX = 3600  # Tiempo en segundos (una hora)
LAMBDA_LLEGADAS = 0.2  # Tasa de llegada media (vehículos por segundo)
FACTOR_TIEMPO = 86400  # Escala para acelerar el tiempo (86400 representa que 1 segundo = 1 día)

# Variables globales
tanque_gasolina = CAPACIDAD_TANQUE_GASOLINA
tanque_diesel = CAPACIDAD_TANQUE_DIESEL
vehiculos_atendidos_gasolina = 0
vehiculos_atendidos_diesel = 0
tiempos = []
niveles_gasolina = []
niveles_diesel = []
vehiculos_gasolina = []
vehiculos_diesel = []
contador_gasolina = 0  # Contador para controlar la proporción de llegada

# Clase de la estación de servicio
class EstacionServicio:
    def __init__(self, env):
        self.env = env
        self.dispensador_gasolina = simpy.Resource(env, capacity=3)
        self.dispensador_diesel = simpy.Resource(env, capacity=3)
        self.env.process(self.reabastecer_tanque_gasolina())
        self.env.process(self.reabastecer_tanque_diesel())

    def reabastecer_tanque_gasolina(self):
        global tanque_gasolina
        while True:
            if tanque_gasolina <= UMBRAL_PEDIDO:
                tiempo_llegada = np.random.randint(TIEMPO_REABASTECIMIENTO_MIN, TIEMPO_REABASTECIMIENTO_MAX) / FACTOR_TIEMPO
                yield self.env.timeout(tiempo_llegada)
                tanque_gasolina = CAPACIDAD_TANQUE_GASOLINA
                print(f"Gasolina reabastecida en el tiempo {self.env.now}")

            yield self.env.timeout(60 / FACTOR_TIEMPO)  # Revisar cada minuto

    def reabastecer_tanque_diesel(self):
        global tanque_diesel
        while True:
            if tanque_diesel <= UMBRAL_PEDIDO:
                tiempo_llegada = np.random.randint(TIEMPO_REABASTECIMIENTO_MIN, TIEMPO_REABASTECIMIENTO_MAX) / FACTOR_TIEMPO
                yield self.env.timeout(tiempo_llegada)
                tanque_diesel = CAPACIDAD_TANQUE_DIESEL
                print(f"Diésel reabastecido en el tiempo {self.env.now}")

            yield self.env.timeout(60 / FACTOR_TIEMPO)  # Revisar cada minuto

    def atender_vehiculo(self, tipo_combustible):
        global tanque_gasolina, tanque_diesel, vehiculos_atendidos_gasolina, vehiculos_atendidos_diesel
        tiempo_llenado = np.random.randint(TIEMPO_LLENADO_MIN, TIEMPO_LLENADO_MAX) / FACTOR_TIEMPO

        if tipo_combustible == 'gasolina':
            with self.dispensador_gasolina.request() as req:
                yield req
                if tanque_gasolina >= 14:
                    tanque_gasolina -= 14
                    vehiculos_atendidos_gasolina += 1
                    print(f"Vehículo de gasolina atendido en el tiempo {self.env.now}. Nivel gasolina: {tanque_gasolina}")
                yield self.env.timeout(tiempo_llenado)

        elif tipo_combustible == 'diesel':
            with self.dispensador_diesel.request() as req:
                yield req
                if tanque_diesel >= 18:
                    tanque_diesel -= 18
                    vehiculos_atendidos_diesel += 1
                    print(f"Vehículo de diésel atendido en el tiempo {self.env.now}. Nivel diésel: {tanque_diesel}")
                yield self.env.timeout(tiempo_llenado)

def llegada_vehiculos(env, estacion):
    global contador_gasolina
    while True:
        # Número de llegadas en el próximo intervalo de un segundo usando distribución Poisson
        num_llegadas = np.random.poisson(LAMBDA_LLEGADAS)
        
        for _ in range(num_llegadas):
            # Definir el tipo de combustible según la proporción 10:1
            if contador_gasolina < 10:
                tipo_combustible = 'gasolina'
                contador_gasolina += 1
            else:
                tipo_combustible = 'diesel'
                contador_gasolina = 0  # Reiniciar el contador

            env.process(estacion.atender_vehiculo(tipo_combustible))

            # Guardar datos para las gráficas
            tiempos.append(env.now)
            niveles_gasolina.append(tanque_gasolina)
            niveles_diesel.append(tanque_diesel)
            vehiculos_gasolina.append(vehiculos_atendidos_gasolina)
            vehiculos_diesel.append(vehiculos_atendidos_diesel)

        # Intervalo de llegada de 1 segundo (equivalente a 1 día en la simulación)
        yield env.timeout(1 / FACTOR_TIEMPO)

# Configuración de la simulación
env = simpy.Environment()
estacion = EstacionServicio(env)
env.process(llegada_vehiculos(env, estacion))

# Función para actualizar la animación
def actualizar_grafico(i):
    ax1.clear()
    ax2.clear()
    ax1.plot(tiempos[:i], niveles_gasolina[:i], label="Nivel Gasolina")
    ax1.plot(tiempos[:i], niveles_diesel[:i], label="Nivel Diésel")
    ax1.set_xlabel("Tiempo (s)")
    ax1.set_ylabel("Inventario (galones)")
    ax1.set_title("Inventario de Combustible")
    ax1.legend(loc="upper right")

    ax2.plot(tiempos[:i], vehiculos_gasolina[:i], label="Vehículos Gasolina")
    ax2.plot(tiempos[:i], vehiculos_diesel[:i], label="Vehículos Diésel")
    ax2.set_xlabel("Tiempo (s)")
    ax2.set_ylabel("Vehículos Atendidos")
    ax2.set_title("Vehículos Atendidos")
    ax2.legend(loc="upper right")

# Configuración de gráficos
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Ejecutar la simulación y animación
env.run(until=86400 / FACTOR_TIEMPO)  # Ejecutar la simulación rápida por 1 día en tiempo real
print("Número de cuadros (frames):", len(tiempos))
ani = animation.FuncAnimation(fig, actualizar_grafico, frames=len(tiempos), interval=10, repeat=False)

plt.tight_layout()
plt.show()
