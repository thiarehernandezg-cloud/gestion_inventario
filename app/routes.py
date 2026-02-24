from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__, 
            template_folder='../templates', 
            static_folder='../static')

# Solo una vez y siempre usando os.getenv
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# --- CONFIGURACIÓN DE LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    db = conectar_db()
    res = db.execute('SELECT * FROM usuarios WHERE id = ?', (user_id,)).fetchone()
    db.close()
    if res:
        return User(res['id'], res['username'])
    return None

def conectar_db():
    ruta_db = os.path.join(os.path.dirname(__file__), '..', 'database.db')
    conexion = sqlite3.connect(ruta_db)
    conexion.row_factory = sqlite3.Row
    return conexion

# --- RUTAS DE AUTENTICACIÓN ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = conectar_db()
        user_db = db.execute('SELECT * FROM usuarios WHERE username = ?', (username,)).fetchone()
        db.close()
        if user_db and check_password_hash(user_db['password'], password):
            user_obj = User(user_db['id'], user_db['username'])
            login_user(user_obj)
            return redirect(url_for('index'))
        flash('Usuario o contraseña incorrectos')
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        db = conectar_db()
        try:
            db.execute('INSERT INTO usuarios (username, password) VALUES (?, ?)', (username, password))
            db.commit()
            return redirect(url_for('login'))
        except:
            flash('El nombre de usuario ya existe')
        finally:
            db.close()
    return render_template('registro.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- RUTAS DE GESTIÓN (PROTEGIDAS) ---

@app.route('/')
@login_required
def index():
    db = conectar_db()
    productos = db.execute('SELECT * FROM productos').fetchall()
    
    res_total = db.execute('SELECT SUM(cantidad) FROM productos').fetchone()
    total_unidades = res_total[0] if res_total[0] else 0
    
    res_bajo = db.execute('SELECT COUNT(*) FROM productos WHERE cantidad <= stock_minimo').fetchone()
    conteo_bajo = res_bajo[0] if res_bajo[0] else 0
    
    db.close()
    return render_template('index.html', 
                           productos=productos, 
                           total_items=total_unidades, 
                           bajo_stock=conteo_bajo)

@app.route('/agregar', methods=['POST'])
@login_required
def agregar():
    nombre = request.form['nombre']
    cantidad = int(request.form['cantidad'])
    stock_minimo = int(request.form['stock_minimo'])
    db = conectar_db()
    db.execute('INSERT INTO productos (nombre, cantidad, stock_minimo) VALUES (?, ?, ?)',
               (nombre, cantidad, stock_minimo))
    db.commit()
    db.close()
    return redirect(url_for('index'))

@app.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    db = conectar_db()
    db.execute('DELETE FROM productos WHERE id = ?', (id,))
    db.commit()
    db.close()
    return redirect(url_for('index'))

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    db = conectar_db()
    if request.method == 'POST':
        nueva_cantidad = request.form['cantidad']
        nuevo_minimo = request.form['stock_minimo']
        db.execute('UPDATE productos SET cantidad = ?, stock_minimo = ? WHERE id = ?', 
                   (nueva_cantidad, nuevo_minimo, id))
        db.commit()
        db.close()
        return redirect(url_for('index'))
    
    producto = db.execute('SELECT * FROM productos WHERE id = ?', (id,)).fetchone()
    db.close()
    return render_template('editar.html', producto=producto)

@app.route('/exportar')
@login_required
def exportar():
    db = conectar_db()
    df = pd.read_sql_query("SELECT nombre, cantidad, stock_minimo, fecha FROM productos", db)
    db.close()
    nombre_archivo = "inventario_pyme.xlsx"
    df.to_excel(nombre_archivo, index=False)
    return send_file(nombre_archivo, as_attachment=True)