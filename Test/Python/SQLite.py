import sqlite3


def createDB():   #creando base de datos (abrir y cerrar)
   conn = sqlite3.connect("Muestras.db") #para conectar
   conn.commit()  #es realizar
   conn.close()  #para cerrar


def createTable():  #creando tabla en base de datos
   conn = sqlite3.connect("Muestras.db")
   cursor = conn.cursor()  #para moverse en la tabla

   cursor.execute(  #estableciendo las columnas de la tabla
      """CREATE TABLE IF NOT EXISTS MUESTRAS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            autor text,
            canal integer,
            unidades integer,
            temperatura_ambiente REAL,
            temperatura REAL,
            fecha_hora TEXT
      )"""
   )
   conn.commit()
   conn.close()


def insertRow(autor, canal, unidades, temperatura_ambiente, temperatura,fecha_hora):
   conn = sqlite3.connect("Muestras.db")
   cursor = conn.cursor()
   instruccion = f"INSERT INTO Muestras VALUES ('{autor}', '{canal}', {unidades}, {temperatura_ambiente},{temperatura},{fecha_hora})"
   cursor.execute(instruccion)
   conn.commit()
   conn.close()

def eliminartabla():
   conn = sqlite3.connect("Muestras.db")
   cursor = conn.cursor()
   instruccion = f"drop table MUESTRAS"
   cursor.execute(instruccion)
   conn.commit()
   conn.close()
   
def readRows():
   conn = sqlite3.connect("Muestras.db")
   cursor = conn.cursor()
   instruccion = f"SELECT * FROM Muestras"
   cursor.execute(instruccion)
   datos = cursor.fetchall()
   conn.commit()
   conn.close()   
   print(datos)


def insertRows(MuestrasList):
   conn = sqlite3.connect("Muestras.db")
   cursor = conn.cursor()
   instruccion = f"INSERT INTO Muestras VALUES (?, ?, ?, ?, ?, ?, NULL)"
   cursor.executemany(instruccion, MuestrasList)
   conn.commit()
   conn.close()

if __name__ == "__main__":  #para despues llamar las funciones
   #createDB()
   eliminartabla()  #para eliminar la tabla
   createTable()
   #insertRow("Jose", "9/30/2023", 1, 0.001, 1.25)
   #readRows()
   """Muestras = [
      ("Jose", "9/30/2023", 1, 0.001, 1.25),
      ("Carlos", "9/30/2023", 2, 0.001, 1.25),
      ("Alpizar", "9/30/2023", 1, 0.001, 1.25)
   ]
   insertRows(Muestras)"""