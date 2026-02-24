import sqlite3

def preparar_db_profesional():
    conexion = sqlite3.connect('database.db')
    cursor = conexion.cursor()

    # Eliminamos tablas viejas para empezar de cero con el modelo relacional.
    cursor.execute('DROP TABLE IF EXISTS movimientos')
    cursor.execute('DROP TABLE IF EXISTS productos')
    cursor.execute('DROP TABLE IF EXISTS usuarios')

    # 1. Tabla de Usuarios
    cursor.execute('''
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'admin'
        )
    ''')

    # 2. Tabla de Productos
    cursor.execute('''
        CREATE TABLE productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL DEFAULT 0,
            stock_minimo INTEGER NOT NULL DEFAULT 0,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. Tabla de Movimientos (La trazabilidad)
    cursor.execute('''
        CREATE TABLE movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            tipo TEXT CHECK(tipo IN ('entrada', 'salida')) NOT NULL,
            cantidad INTEGER NOT NULL,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (producto_id) REFERENCES productos (id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')

    conexion.commit()
    conexion.close()
    print("Base de datos  lista.")

if __name__ == '__main__':
    preparar_db_profesional()