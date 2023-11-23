import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import sqlite3
from datetime import datetime
import serial
import time
from collections import deque
import threading
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

now = datetime.now()


# Configura la comunicación con el Arduino
arduino_port = "COM5"  # Cambia esto al puerto de tu Arduino
baud_rate = 9600  # Asegúrate de que coincida con la configuración de tu Arduino

arduino = serial.Serial(arduino_port, baud_rate)

# Inicializar las listas para almacenar datos de los canales
buffer_length = 80  # Número de datos a mantener en el búfer
valores_canal1 = []
valores_canal2 = []
valor_ta = 0
tiempos = []

buffer_valores_canal1 = deque(maxlen=buffer_length)
buffer_valores_canal2 = deque(maxlen=buffer_length)
buffer_tiempos = deque(maxlen=buffer_length)

valor1 = 0 
valor2 = 0
tiempo_actual = 0

canal1_seleccionado = True
canal2_seleccionado = True

# Variables para el control de la grabación de datos en SQLite3
grabando_datos = False
datos_grabados = []  # Lista para almacenar datos grabados


def leer_datos_desde_arduino():
    global valor_ta, valor1, valor2
    while True:
        try:
            # Leer datos desde el Arduino
            while arduino.in_waiting:
                linea = arduino.readline().decode().strip().split(',')
                if len(linea) == 3:
                    valor1, valor2, valor3 = map(float, linea)
                    valores_canal1.append(valor1)
                    valores_canal2.append(valor2)
                    valor_ta = valor3
                    tiempos.append(tiempo_transcurrido())
                    
                    

            # Dormir durante 500 microsegundos antes de la próxima lectura
            time.sleep(0.05)
        except serial.SerialException:
            print("Error de lectura desde el Arduino.")
            break
        
           
def actualizar_interfaz_grafica():
    
    buffer_valores_canal1.append(valor1)
    buffer_valores_canal2.append(valor2)
        
    buffer_tiempos.append(tiempo_transcurrido())
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    
    tiempo_actual = tiempo_transcurrido()  # Calcular el tiempo actual una vez
    tiempo_inicial = max(tiempo_actual - 20, 0) if buffer_tiempos else max(tiempo_actual - 20, 0)
    
    ax.clear()  # Borrar el gráfico

    if mostrar_entrada.get() == 0:
        tiempos_recortados = [t - tiempo_inicial for t in buffer_tiempos if t >= tiempo_inicial]
        valores_recortados_canal1 = [buffer_valores_canal1[i] for i in range(len(buffer_tiempos)) if buffer_tiempos[i] >= tiempo_inicial]
        ax.plot(tiempos_recortados, valores_recortados_canal1, label='Canal 1')
        ax.set_ylabel('Valor')
        ax.set_title('Datos del Canal 1')
    elif mostrar_entrada.get() == 1:
        tiempos_recortados = [t - tiempo_inicial for t in buffer_tiempos if t >= tiempo_inicial]
        valores_recortados_canal2 = [buffer_valores_canal2[i] for i in range(len(buffer_tiempos)) if buffer_tiempos[i] >= tiempo_inicial]
        ax.plot(tiempos_recortados, valores_recortados_canal2, label='Canal 2')
        ax.set_ylabel('Valor')
        ax.set_title('Datos del Canal 2')
    elif mostrar_entrada.get() == 2:
        tiempos_recortados = [t - tiempo_inicial for t in buffer_tiempos if t >= tiempo_inicial]
        valores_recortados_canal1 = [buffer_valores_canal1[i] for i in range(len(buffer_tiempos)) if buffer_tiempos[i] >= tiempo_inicial]
        valores_recortados_canal2 = [buffer_valores_canal2[i] for i in range(len(buffer_tiempos)) if buffer_tiempos[i] >= tiempo_inicial]
        ax.plot(tiempos_recortados, valores_recortados_canal1, label='Canal 1')
        ax.plot(tiempos_recortados, valores_recortados_canal2, label='Canal 2')
        ax.set_ylabel('Valor')
        ax.set_title('Datos de Canales 1 y 2')
    
    ax.set_xlim(0, 20)  # Configurar el límite del eje x
    ax.legend(loc='lower right')
    canvas.draw()
    
    # Actualizar las etiquetas de nombre y unidades
    nombre_label.config(text=f"Nombre: {nombre_autor.get()}")
    unidades_label.config(text=f"Unidades: {unidades.get()}")
    
    if grabando_datos:
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        datos_grabados.append((nombre_autor.get(), fecha_actual, 'canal1', unidades.get(), valores_canal1[-1], valor_ta))
        datos_grabados.append((nombre_autor.get(),fecha_actual, 'canal2', unidades.get(), valores_canal2[-1], valor_ta))
    # Programar la próxima actualización después de 1000 milisegundos (1 segundo)
    root.after(1000, actualizar_interfaz_grafica)
        
# Función para iniciar o detener la grabación de datos
def control_grabacion():
    global grabando_datos
    grabando_datos = not grabando_datos
    if grabando_datos:
        start_button.config(text="Detener Grabación")
    else:
        start_button.config(text="Iniciar Grabación")
        if datos_grabados:
            guardar_muestras_en_sqlite(datos_grabados)
            datos_grabados.clear()

# Función para obtener el tiempo transcurrido en segundos desde el inicio
def tiempo_transcurrido():
    return (datetime.now() - tiempo_inicio).total_seconds()

# Variables para almacenar la última lectura válida de cada canal
ultimo_valor1 = None
ultimo_valor2 = None

# Función para convertir voltaje a temperatura (ejemplo)
def voltaje_a_temperatura(voltaje):
    # Aquí puedes implementar tu propia lógica de conversión
    # En este ejemplo, se asume que la temperatura aumenta con el voltaje
    return voltaje * 20  # Supone una relación lineal entre voltaje y temperatura

# Función para guardar muestras en SQLite3
def guardar_muestras_en_sqlite(muestras):
    conn = sqlite3.connect('Muestras.db')
    cursor = conn.cursor()
    try:
        # Modificando la consulta para incluir la fecha actual
        cursor.executemany(
            "INSERT INTO MUESTRAS (autor, canal, unidades, temperatura_ambiente, temperatura_real, fecha_hora) VALUES (?, ?, ?, ?, ?, ?, NULL)",
            [(m[0], m[1] , m[2], m[3], m[4], m[5]) for m in muestras]
        )
        conn.commit()
        print("Datos guardados en SQLite3.")
    except Exception as e:
        conn.rollback()
        print(f"Error al guardar datos en SQLite3: {e}")
    finally:
        conn.close()


# Función para enviar datos de escala y canal al Arduino
def enviar_datos_arduino():
    
    # Obtener la escala seleccionada y el canal seleccionado
    escala_seleccionada = escala_var.get()
    canal_seleccionado = canal_var.get()
    canal1_seleccionado = canal1_activado.get()
    canal2_seleccionado = canal2_activado.get()
   
    # Formatear la cadena para enviar al Arduino
    datos = f"{escala_seleccionada},{canal_seleccionado},{canal1_seleccionado},{canal2_seleccionado},\n"
    arduino.write(datos.encode())  # Enviar la cadena al Arduino
    print(canal2_seleccionado)
   

# Crear una ventana
root = tk.Tk()
root.title("Visualizador de Datos")

# Inicializar las listas para almacenar datos simulados
tiempo_inicio = datetime.now()

# Crear el marco para las gráficas
frame = ttk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

# Crear una variable de control para mostrar ambas entradas o una sola
mostrar_entrada = tk.IntVar()
mostrar_entrada.set(2)  # Mostrar ambos Canales por defecto

# Crear una variable de control para la configuración del Canal 1
canal1_activado = tk.BooleanVar()
canal1_activado.set(True)

canal1_convertir_temperatura = tk.BooleanVar()
canal1_convertir_temperatura.set(False)

canal1_escala = tk.IntVar()
canal1_escala.set(1)

# Crear una variable de control para la configuración del Canal 2
canal2_activado = tk.BooleanVar()
canal2_activado.set(True)

canal2_convertir_temperatura = tk.BooleanVar()
canal2_convertir_temperatura.set(False)

canal2_escala = tk.IntVar()
canal2_escala.set(1)

# Crear una variable para el nombre del autor
nombre_autor = tk.StringVar()
nombre_autor.set("Tu Nombre")

# Crear una variable para las unidades
unidades = tk.StringVar()
unidades.set("Unidades")

# Crear una entrada para el nombre del autor
nombre_entry = ttk.Entry(frame, textvariable=nombre_autor)
nombre_entry.grid(row=0, column=1, padx=10, pady=5, sticky='w')

# Crear una entrada para las unidades
unidades_entry = ttk.Entry(frame, textvariable=unidades)
unidades_entry.grid(row=1, column=1, padx=10, pady=5, sticky='w')

# Crear etiquetas para mostrar nombre y unidades
nombre_label = ttk.Label(frame, text=f"Nombre: {nombre_autor.get()}")
nombre_label.grid(row=0, column=2, padx=10, pady=5, sticky='w')

unidades_label = ttk.Label(frame, text=f"Unidades: {unidades.get()}")
unidades_label.grid(row=1, column=2, padx=10, pady=5, sticky='w')

# Botón para iniciar o detener la grabación de datos
start_button = ttk.Button(frame, text="Iniciar Grabación", command=control_grabacion)
start_button.grid(row=2, column=1, padx=10, pady=10, sticky='w')

# Crear los botones de selección para mostrar datos de los canales
ttk.Radiobutton(frame, text="Canal 1", variable=mostrar_entrada, value=0).grid(row=3, column=0, padx=10, pady=5, sticky='w')
ttk.Radiobutton(frame, text="Canal 2", variable=mostrar_entrada, value=1).grid(row=4, column=0, padx=10, pady=5, sticky='w')
ttk.Radiobutton(frame, text="Ambos Canales", variable=mostrar_entrada, value=2).grid(row=5, column=0, padx=10, pady=5, sticky='w')

# Crear el gráfico
fig = Figure(figsize=(8, 4))
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=frame)
canvas.get_tk_widget().grid(row=0, column=3, rowspan=7, columnspan=1, padx=10, pady=10, sticky='nsew')

# Botones para la configuración del Canal 1
ttk.Checkbutton(frame, text="Activar Canal 1", variable=canal1_activado, command=enviar_datos_arduino).grid(row=0, column=4, padx=10, pady=5, sticky='w')
ttk.Checkbutton(frame, text="Convertir a °C", variable=canal1_convertir_temperatura).grid(row=1, column=4, padx=10, pady=5, sticky='w')


# Botones para la configuración del Canal 2
ttk.Checkbutton(frame, text="Activar Canal 2", variable=canal2_activado, command=enviar_datos_arduino).grid(row=0, column=5, padx=10, pady=5, sticky='w')
ttk.Checkbutton(frame, text="Convertir a °C", variable=canal2_convertir_temperatura).grid(row=1, column=5, padx=10, pady=5, sticky='w')

# Crear una variable de control para la selección de escala y canal
escala_var = tk.IntVar()
canal_var = tk.IntVar()

# Crear un menú desplegable para seleccionar la escala
ttk.Label(frame, text="Seleccionar Escala:").grid(row=4, column=4, padx=10, pady=5, sticky='w')
escala_menu = ttk.OptionMenu(frame, escala_var, 0, 0, 1, 2, 3, 4, 5)
escala_menu.grid(row=4, column=5, padx=10, pady=5, sticky='w')

# Crear un menú desplegable para seleccionar el canal
ttk.Label(frame, text="Seleccionar Canal:").grid(row=5, column=4, padx=10, pady=5, sticky='w')
canal_menu = ttk.OptionMenu(frame, canal_var, 1, 1, 2)
canal_menu.grid(row=5, column=5, padx=10, pady=5, sticky='w')

# Botón para enviar los datos al Arduino
enviar_button = ttk.Button(frame, text="Enviar a Arduino", command=enviar_datos_arduino)
enviar_button.grid(row=6, column=4, columnspan=2, padx=10, pady=10, sticky='w')

lector_arduino = threading.Thread(target=leer_datos_desde_arduino)
lector_arduino.daemon = True  # El hilo se cerrará cuando se cierre la aplicación principal
lector_arduino.start()


# Llamar a la función para iniciar la actualización de la interfaz gráfica
actualizar_interfaz_grafica()

root.mainloop()

# Asegúrate de cerrar la conexión con el Arduino cuando finalices
arduino.close()
