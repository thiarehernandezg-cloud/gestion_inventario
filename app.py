from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def conectar_db():
    conexion = sqlite3.connect('database.db')
    conexion.row_factory = sqlite3.Row
    return conexion

@app.route('/')
def index():
    db = conectar_db()
    productos = db.execute('SELECT * FROM productos').fetchall()
    db.close()
    return render_template('index.html', productos=productos)

@app.route('/agregar', methods=['POST'])
def agregar():
    nombre = request.form['nombre']
    cantidad = int(request.form['cantidad'])
    stock_minimo = int(request.form['stock_minimo'])
    
    db = conectar_db()
    db.execute('INSERT INTO productos (nombre, cantidad, stock_minimo) VALUES (?, ?, ?)',
               (nombre, cantidad, stock_minimo))
    db.commit()
    db.close()
    return redirect('/')

@app.route('/eliminar/<int:id>')
def eliminar(id):
    db = conectar_db()
    db.execute('DELETE FROM productos WHERE id = ?', (id,))
    db.commit()
    db.close()
    return redirect('/')
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    db = conectar_db()
    if request.method == 'POST':
        nueva_cantidad = request.form['cantidad']
        nuevo_minimo = request.form['stock_minimo']
        db.execute('UPDATE productos SET cantidad = ?, stock_minimo = ? WHERE id = ?', 
                   (nueva_cantidad, nuevo_minimo, id))
        db.commit()
        db.close()
        return redirect('/')
    
    # Si es GET, mostramos el formulario con los datos actuales
    producto = db.execute('SELECT * FROM productos WHERE id = ?', (id,)).fetchone()
    db.close()
    return render_template('editar.html', producto=producto)
if __name__ == '__main__':
    app.run(debug=True)