import sqlite3

def preparar_db():
    conexion = sqlite3.connect('database.db')
    cursor = conexion.cursor()

    # Crea tabla de productos si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            stock_minimo INTEGER NOT NULL,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Crea tabla de usuarios para el Login
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    conexion.commit()
    conexion.close()
    print("¡Tablas de productos y usuarios listas!")

if __name__ == '__main__':
    preparar_db()