import simpy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Parámetros de la simulación
TIEMPO_LLENADO_MIN = 20  # en segundos
TIEMPO_LLENADO_MAX = 40
CAPACIDAD_TANQUE_GASOLINA = 12000  # en galones
CAPACIDAD_TANQUE_DIESEL = 12000
UMBRAL_PEDIDO = 8000  # Umbral para solicitar reabastecimiento ajustado a 8000 galones
TIEMPO_REABASTECIMIENTO_MIN = 1800  # Tiempo en segundos (media hora)
TIEMPO_REABASTECIMIENTO_MAX = 3600  # Tiempo en segundos (una hora)
LAMBDA_LLEGADAS = 0.2  # Tasa de llegada media (vehículos por segundo)
FACTOR_TIEMPO = 1000  # Escala para ralentizar el tiempo (86400 representa que 1 segundo = 1 día)

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
uso_dispensador1_gasolina = []
uso_dispensador1_diesel = []
uso_dispensador2_gasolina = []
uso_dispensador2_diesel = []
uso_dispensador3_diesel = []
contador_gasolina = 0  # Contador para controlar la proporción de llegada

# Clase de la estación de servicio
class EstacionServicio:
    def __init__(self, env):
        self.env = env
        # Configuración de los tres dispensadores
        self.dispensador1 = simpy.Resource(env, capacity=4)  # Dispensador 1 (4 gasolina, 2 diésel)
        self.dispensador2 = simpy.Resource(env, capacity=4)  # Dispensador 2 (4 gasolina, 2 diésel)
        self.dispensador3 = simpy.Resource(env, capacity=2)  # Dispensador 3 (solo 2 diésel)

        # Contadores de vehículos en cada dispensador
        self.contador_dispensador1_gasolina = 0
        self.contador_dispensador1_diesel = 0
        self.contador_dispensador2_gasolina = 0
        self.contador_dispensador2_diesel = 0
        self.contador_dispensador3_diesel = 0

        # Procesos de reabastecimiento
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

        # Asignación equilibrada para gasolina y diésel en dispensadores 1 y 2
        if tipo_combustible == 'gasolina':
            if self.dispensador1.count < 4 and self.dispensador2.count < 4:
                dispensador = self.dispensador1 if (vehiculos_atendidos_gasolina % 2 == 0) else self.dispensador2
            elif self.dispensador1.count < 4:
                dispensador = self.dispensador1
            else:
                dispensador = self.dispensador2

            with dispensador.request() as req:
                yield req
                if tanque_gasolina >= 14:
                    tanque_gasolina -= 14
                    vehiculos_atendidos_gasolina += 1
                    if dispensador == self.dispensador1:
                        self.contador_dispensador1_gasolina += 1
                    else:
                        self.contador_dispensador2_gasolina += 1
                    print(f"Vehículo de gasolina atendido en el tiempo {self.env.now}. Nivel gasolina: {tanque_gasolina}")
                yield self.env.timeout(tiempo_llenado)
                # Reducir el contador después de atender
                if dispensador == self.dispensador1:
                    self.contador_dispensador1_gasolina -= 1
                else:
                    self.contador_dispensador2_gasolina -= 1

        elif tipo_combustible == 'diesel':
            if self.dispensador1.count < 2 and self.dispensador2.count < 2:
                dispensador = self.dispensador1 if (vehiculos_atendidos_diesel % 2 == 0) else self.dispensador2
            elif self.dispensador1.count < 2:
                dispensador = self.dispensador1
            elif self.dispensador2.count < 2:
                dispensador = self.dispensador2
            else:
                dispensador = self.dispensador3

            with dispensador.request() as req:
                yield req
                if tanque_diesel >= 18:
                    tanque_diesel -= 18
                    vehiculos_atendidos_diesel += 1
                    if dispensador == self.dispensador1:
                        self.contador_dispensador1_diesel += 1
                    elif dispensador == self.dispensador2:
                        self.contador_dispensador2_diesel += 1
                    else:
                        self.contador_dispensador3_diesel += 1
                    print(f"Vehículo de diésel atendido en el tiempo {self.env.now}. Nivel diésel: {tanque_diesel}")
                yield self.env.timeout(tiempo_llenado)
                # Reducir el contador después de atender
                if dispensador == self.dispensador1:
                    self.contador_dispensador1_diesel -= 1
                elif dispensador == self.dispensador2:
                    self.contador_dispensador2_diesel -= 1
                else:
                    self.contador_dispensador3_diesel -= 1

            # Registrar el estado actual en listas para la gráfica
        uso_dispensador1_gasolina.append(self.contador_dispensador1_gasolina)
        uso_dispensador1_diesel.append(self.contador_dispensador1_diesel)
        uso_dispensador2_gasolina.append(self.contador_dispensador2_gasolina)
        uso_dispensador2_diesel.append(self.contador_dispensador2_diesel)
        uso_dispensador3_diesel.append(self.contador_dispensador3_diesel)

def llegada_vehiculos(env, estacion):
    global contador_gasolina
    while True:
        num_llegadas = np.random.poisson(LAMBDA_LLEGADAS)
        
        for _ in range(num_llegadas):
            if contador_gasolina < 10:
                tipo_combustible = 'gasolina'
                contador_gasolina += 1
            else:
                tipo_combustible = 'diesel'
                contador_gasolina = 0

            env.process(estacion.atender_vehiculo(tipo_combustible))

            # Guardar datos para las gráficas
            tiempos.append(env.now)
            niveles_gasolina.append(tanque_gasolina)
            niveles_diesel.append(tanque_diesel)
            vehiculos_gasolina.append(vehiculos_atendidos_gasolina)
            vehiculos_diesel.append(vehiculos_atendidos_diesel)

        yield env.timeout(1 / FACTOR_TIEMPO)

# Configuración de la simulación
env = simpy.Environment()
estacion = EstacionServicio(env)
env.process(llegada_vehiculos(env, estacion))

# Función para actualizar la animación de todas las gráficas en una sola ventana
def actualizar_grafico(i):
    ax1.clear()
    ax2.clear()
    ax3.clear()
    ax4.clear()
    ax5.clear()

    step = 10
    end_index = i * step

    # Gráfica de inventario de combustible
    ax1.plot(tiempos[:end_index], niveles_gasolina[:end_index], label="Nivel Gasolina")
    ax1.plot(tiempos[:end_index], niveles_diesel[:end_index], label="Nivel Diésel")
    ax1.set_xlabel("Tiempo (s)")
    ax1.set_ylabel("Inventario (galones)")
    ax1.set_title("Inventario de Combustible")
    ax1.legend(loc="upper right")

    # Gráfica de vehículos atendidos
    ax2.plot(tiempos[:end_index], vehiculos_gasolina[:end_index], label="Vehículos Gasolina")
    ax2.plot(tiempos[:end_index], vehiculos_diesel[:end_index], label="Vehículos Diésel")
    ax2.set_xlabel("Tiempo (s)")
    ax2.set_ylabel("Vehículos Atendidos")
    ax2.set_title("Vehículos Atendidos")
    ax2.legend(loc="upper right")

    # Gráficas de uso de cada dispensador
    ax3.plot(tiempos[:end_index], uso_dispensador1_gasolina[:end_index], label="Gasolina")
    ax3.plot(tiempos[:end_index], uso_dispensador1_diesel[:end_index], label="Diésel")
    ax3.set_xlabel("Tiempo (s)")
    ax3.set_ylabel("Vehículos en Dispensador 1")
    ax3.set_title("Uso del Dispensador 1")
    ax3.legend(loc="upper right")

    ax4.plot(tiempos[:end_index], uso_dispensador2_gasolina[:end_index], label="Gasolina")
    ax4.plot(tiempos[:end_index], uso_dispensador2_diesel[:end_index], label="Diésel")
    ax4.set_xlabel("Tiempo (s)")
    ax4.set_ylabel("Vehículos en Dispensador 2")
    ax4.set_title("Uso del Dispensador 2")
    ax4.legend(loc="upper right")

    ax5.plot(tiempos[:end_index], uso_dispensador3_diesel[:end_index], label="Diésel")
    ax5.set_xlabel("Tiempo (s)")
    ax5.set_ylabel("Vehículos en Dispensador 3")
    ax5.set_title("Uso del Dispensador 3")
    ax5.legend(loc="upper right")

# Configuración de gráficos en una sola ventana
fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(5, 1, figsize=(10, 15))

# Ejecutar la simulación
env.run(until=43200 / FACTOR_TIEMPO)  # Ejecutar solo 12 horas

# Configuración de la animación para avanzar rápidamente
ani = animation.FuncAnimation(fig, actualizar_grafico, frames=len(tiempos) // 10, interval=1, repeat=False)

plt.tight_layout()
plt.show()