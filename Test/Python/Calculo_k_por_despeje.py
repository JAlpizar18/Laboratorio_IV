import sqlite3
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt

def calcular_k(base_datos):
    # Obtener datos de la base de datos
    conn = sqlite3.connect(base_datos)
    cursor = conn.cursor()
    cursor.execute('SELECT temperatura, temperatura_ambiente, fecha_hora FROM DatosTemperatura')
    filas = cursor.fetchall()
    conn.close()

    # Desempaquetar datos
    temperaturas, temperaturas_ambiente, fechas = zip(*filas)

    # Convertir fechas a diferencia de tiempo en segundos
    fechas = [datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S') for fecha in fechas]
    diferencia_tiempo = [(fecha - fechas[0]).total_seconds() for fecha in fechas]

    # Convertir temperaturas a un array de numpy
    temperaturas = np.array(temperaturas)
    temps_ambientes = np.array(temperaturas_ambiente)
    # Filtrar los datos del canal 1 (valores impares)
    temperaturas_canal_1 = temperaturas[::2]
    tiempo_canal_1 = np.array(diferencia_tiempo[::2])  # Convertir a array de numpy
    temperaturas_ambiente_canal1 = np.array(temps_ambientes[::2])
    tiempo_canal_1[0] = 1
    
    # Filtrar los datos del canal 2 (valores pares)
    temperaturas_canal_2 = temperaturas[1::2]
    tiempo_canal_2 = np.array(diferencia_tiempo[1::2])  # Convertir a array de numpy
    temperaturas_ambiente_canal2 = np.array(temps_ambientes[1::2])
    tiempo_canal_2[0] = 1
    
    # Imprimir el array de temperaturas_canal_1
    print("tiempos canal 2:", tiempo_canal_2)
    
    # Calcular K para cada par de temperaturas y tiempos para cada canal
   # ...

    # Calcular K para cada par de temperaturas y tiempos para cada canal
    # Manejo de Cero o Valores Negativos
    k_valores_canal_1 = -np.log(np.where((temperaturas_canal_1 - temperaturas_ambiente_canal1) <= 0, 1e-10, (temperaturas_canal_1 - temperaturas_ambiente_canal1)) / (temperaturas_canal_1[0] - temperaturas_ambiente_canal1)) / tiempo_canal_1
    k_valores_canal_2 = -np.log(np.where((temperaturas_canal_2 - temperaturas_ambiente_canal2) <= 0, 1e-10, (temperaturas_canal_2 - temperaturas_ambiente_canal2)) / (temperaturas_canal_2[0] - temperaturas_ambiente_canal2)) / tiempo_canal_2


    # Calcular el valor promedio de K para cada canal
    k_promedio_canal_1 = np.mean(k_valores_canal_1)
    k_promedio_canal_2 = np.mean(k_valores_canal_2)

    print(f"Valor estimado de K para Canal 1: {k_promedio_canal_1:.4f}")
    print(f"Valor estimado de K para Canal 2: {k_promedio_canal_2:.4f}")

# Calcular y mostrar el valor estimado de K para cada canal
calcular_k('datos_temperatura2.db')
