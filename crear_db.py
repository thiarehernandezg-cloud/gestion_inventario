import sqlite3

conexion = sqlite3.connect('database.db')
cursor = conexion.cursor()

# Borramos la tabla vieja para crear la nueva con fecha
cursor.execute('DROP TABLE IF EXISTS productos')

cursor.execute('''
    CREATE TABLE productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        stock_minimo INTEGER NOT NULL,
        fecha DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

conexion.commit()
conexion.close()
print("¡Base de datos actualizada con éxito!")