import time
import threading

import pandas as pd

from simpy import Environment

from PyQt5 import QtCore
from PyQt5.QtCore import QObject

from uci.procesar_datos import *


class Uci(threading.Thread):
    def __init__(self, path: str, diagnostico: list, porcientos: list) -> None:
        super().__init__()

        class Signal(QObject):
            signal_progBarr = QtCore.pyqtSignal(int)
            """Usado para actualizar con un valor la barra de progreso de simulación"""

            signal_terminated = QtCore.pyqtSignal(bool)
            """Usado para enviar señal cuando termine la simulación"""

            signal_tiempo = QtCore.pyqtSignal(float)
            """Usado para el tiempo de simulación resultante."""

        # Se inicializan las variables necesarias para la simulacion
        self.signal = Signal()
        self.index = 0
        self.env = Environment()

        # Se inicializan las variables necesarias para la simulacion
        self.diagnosticos_paciente = diagnostico
        self.porcientos_paciente = porcientos

        # Definicion de las listas para exportar los datos de la simulacion
        self.hora_llegada_hospital = list()
        self.hora_llegada_uci = list()
        self.hora_ini_vam = list()
        self.hora_fin_vam = list()
        self.hora_salida_uci = list()

        self._stop_event = threading.Event()

        # Se comienza a simular
        self.env.process(self.entrada_paciente(path))

    def run(self):
        print("-- Comenzando simulación --")

        t_comienzo = time.time()  # Marcar el tiempo de inicio.
        self.signal.signal_terminated.emit(False)

        # Simulación.
        for i in range(17881):
            self.signal.signal_progBarr.emit(i)
            self.env.run(until=i + 1)
            if self._stop_event.is_set():
                break

        t_final = time.time()  # Marcar el tiempo de finalizacion.
        tiempo_transcurrido = round((t_final - t_comienzo), 1)

        self.signal.signal_progBarr.emit(0)  # Volviendo a 0 la barra de progreso
        self.signal.signal_terminated.emit(True)  # Señal booleana de terminación
        self.signal.signal_tiempo.emit(tiempo_transcurrido)  # Señal con valor de tiempo

        print(f"-- La simulación terminó a los {tiempo_transcurrido} segundos. --")

    def stop(self):
        print("-- Deteniendo la simulación --")
        self._stop_event.set()

    def entrada_paciente(self, path: str):
        """Controla la entrada de cada paciente al hospital."""

        # Se obtienen los datos del archivo de entrada y se agregan a la cola de pacientes
        gen_fecha_ing = get_fecha_ingreso(path)
        next(gen_fecha_ing)
        paciente = 0

        while True:
            paciente += 1
            # print(f"El paciente {paciente} llego al hospital a las {self.env.now}h")

            # Se calcula la espera y se espera hasta que llegue un nuevo paciente
            try:
                fecha_siguiente, fecha = next(gen_fecha_ing)
                self.hora_llegada_hospital.append(self.env.now)
                espera_ingreso = fecha_siguiente - fecha
                self.env.process(self.entrada_paciente_uci(path, paciente))
                yield self.env.timeout(espera_ingreso.days * 24)
            except StopIteration:
                break

    def entrada_paciente_uci(self, path: str, paciente: int):
        """Funcion que controla el tránsito de cada paciente dentro del hospital."""

        # Se inicializan los generadores necesarios
        gen_fecha_ing_uci = get_fecha_ing_uci(path)
        gen_fecha_ingreso = get_fecha_ingreso(path)
        gen_estadia_uci = get_estadia_uci(path)
        gen_tiempo_van = get_tiempo_vam(path)
        gen_diagnostico = get_diagnostico(path)
        gen_fecha_egreso = get_fecha_egreso(path)

        while True:

            # Se calcula el tiempo de espera de entrada a la uci y se espera
            fecha_ing_uci = next(gen_fecha_ing_uci)
            fecha_ingreso = next(gen_fecha_ingreso)
            espera_uci = fecha_ing_uci - fecha_ingreso[1]

            yield self.env.timeout(espera_uci.days * 24)

            # print(f"El paciente {paciente} llega a la uci a las {self.env.now}h")
            self.hora_llegada_uci.append(self.env.now)

            # Se calcula los tiempos antes del van y despues de el y se espera a que se le ponga van
            porcientos = self.porcientos(
                self.diagnosticos_paciente, self.porcientos_paciente
            )
            diagnostico = next(gen_diagnostico)
            estadia_uci = next(gen_estadia_uci)
            tiempo_van = next(gen_tiempo_van)
            espera_antes_vam = int(porcientos[diagnostico] / 100 * estadia_uci * 24)
            espera_despues_vam = estadia_uci * 24 - espera_antes_vam - tiempo_van

            yield self.env.timeout(espera_antes_vam)

            # print(f"El paciente {paciente} se le pone ventilacion artificial a las {self.env.now}h")
            self.hora_ini_vam.append(self.env.now)

            # Se espera el tiempo que el paciente pasa en van

            yield self.env.timeout(tiempo_van)

            # print(f"Al paciente {paciente} se le quita la ventilacion a las {self.env.now}h")
            self.hora_fin_vam.append(self.env.now)

            # Se espera la salida del paciente de la uci

            yield self.env.timeout(espera_despues_vam)

            # Se decide a que sala ira el paciente
            gen_sala_egreso = get_sala_egreso(path)
            sala_egreso = next(gen_sala_egreso)
            # print(f"El paciente {paciente} salio de la uci a las {self.env.now}h y fue trasladado hacia {sala_egreso}")
            self.hora_salida_uci.append(self.env.now)

            # Se espera el egreso del paciente
            fecha_egreso = next(gen_fecha_egreso)
            t = fecha_egreso - fecha_ingreso[1] - espera_uci
            espera_egreso = t.days - estadia_uci

            yield self.env.timeout(espera_egreso * 24)

            # Se termina la simulacion
            gen_evolucion = get_evolucion(path)
            evolucion = next(gen_evolucion)

            if evolucion == "vivo":
                # print(f"El paciente {paciente} se mantiene vivo y fue dado de alta a las {self.env.now}h")
                break
            else:
                # print(f"El paciente {paciente} fallece a las {self.env.now}h")
                break

    def porcientos(self, diagnosticos: list, porcientos: list):
        diccionario = dict(zip(diagnosticos, porcientos))
        return diccionario

    def exportar_datos(self):
        data = {
            "Hora_llegada_hospital": self.hora_llegada_hospital,
            "Hora_llegada_uci": self.hora_llegada_uci,
            "Hora_inicio_vam": self.hora_ini_vam,
            "Hora_final_vam": self.hora_fin_vam,
            "Hora_salida_uci": self.hora_salida_uci,
        }
        dataFrame = pd.DataFrame(data)
        dataFrame.to_csv("Datos de simulacion.csv", index=False)
