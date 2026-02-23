import sqlite3
conexion = sqlite3.connect('database.db')
cursor = conexion.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        stock_minimo INTEGER NOT NULL
    )
''')
conexion.commit()
conexion.close()
print("¡Tabla 'productos' creada exitosamente!")