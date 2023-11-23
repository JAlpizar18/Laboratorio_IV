import sqlite3
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize

import sqlite3
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize

def ajustar_curva(base_datos):
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
    temperaturas_ambiente = np.array(temperaturas_ambiente)

    # Valor fijo para T_0 (tomando el primer valor de la columna de temperaturas)
    T_0 = temperaturas[0]

    # Ajuste de la curva solo para estimar K en el canal 1
    params_canal_1, _ = scipy.optimize.curve_fit(lambda t, k: temperaturas_ambiente[::2] + (T_0 - temperaturas_ambiente[::2]) * np.exp(-k * t),
                                         diferencia_tiempo[::2], temperaturas[::2])

    # Ajuste de la curva solo para estimar K en el canal 2
    params_canal_2, _ = scipy.optimize.curve_fit(lambda t, k: temperaturas_ambiente[1::2] + (T_0 - temperaturas_ambiente[1::2]) * np.exp(-k * t),
                                         diferencia_tiempo[1::2], temperaturas[1::2])

    # Desempaquetar los parámetros ajustados K
    k_estimado_canal_1 = params_canal_1[0]
    k_estimado_canal_2 = params_canal_2[0]

    # Mostrar el valor estimado de K en un recuadro sobre la gráfica
    plt.plot(diferencia_tiempo, temperaturas, label='Datos reales')
    
    # Graficar los datos utilizados para K en el canal 1
    plt.scatter(diferencia_tiempo[::2], temperaturas[::2], color='red', marker='o', label='Datos Canal 1')

    # Graficar los datos utilizados para K en el canal 2
    plt.scatter(diferencia_tiempo[1::2], temperaturas[1::2], color='blue', marker='x', label='Datos Canal 2')

    texto_k_canal_1 = f'Estimado K Canal 1: {k_estimado_canal_1:.4f}'
    texto_k_canal_2 = f'Estimado K Canal 2: {k_estimado_canal_2:.4f}'
    plt.text(0.05, 0.80, texto_k_canal_1, transform=plt.gca().transAxes, bbox=dict(facecolor='white', alpha=0.8))
    plt.text(0.05, 0.75, texto_k_canal_2, transform=plt.gca().transAxes, bbox=dict(facecolor='white', alpha=0.8))

    plt.legend()
    plt.show()

# Ajustar la curva y mostrar la gráfica con el valor estimado de K
ajustar_curva('datos_temperatura3.db')


