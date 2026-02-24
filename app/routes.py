from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import pandas as pd
from dotenv import load_dotenv
import os
# --- CÓDIGO TEMPORAL PARA ACTUALIZAR LA DB ---
def actualizar_base_de_datos():
    db = sqlite3.connect(os.path.join(os.path.dirname(__file__), '..', 'database.db'))
    try:
        db.execute('ALTER TABLE productos ADD COLUMN fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP')
        db.commit()
        print("¡Columna añadida con éxito!")
    except Exception as e:
        print("La columna ya existía o hubo un error:", e)
    finally:
        db.close()

actualizar_base_de_datos() # Esto se ejecutará al iniciar tu app
# --------------------------------------------
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

# --- RUTAS DE GESTIÓN ACTUALIZADAS ---

@app.route('/')
@login_required
def index():
    db = conectar_db()
    
    # 1. Tabla principal de productos
    productos = db.execute('SELECT * FROM productos').fetchall()
    
    # 2. ÚLTIMOS MOVIMIENTOS (Trazabilidad)
    movimientos = db.execute('''
        SELECT m.*, p.nombre as producto_nombre, u.username 
        FROM movimientos m
        JOIN productos p ON m.producto_id = p.id
        JOIN usuarios u ON m.usuario_id = u.id
        ORDER BY m.fecha DESC LIMIT 5
    ''').fetchall()
    
    # --- CÁLCULO DE KPIs PARA EL DASHBOARD ---
    
    # KPI 1: Total de productos (Diferentes SKUs)
    total_skus = db.execute('SELECT COUNT(*) FROM productos').fetchone()[0] or 0
    
    # KPI 2: Productos con stock bajo (Menor o igual al mínimo pero mayor a 0)
    bajo_stock = db.execute('SELECT COUNT(*) FROM productos WHERE cantidad <= stock_minimo AND cantidad > 0').fetchone()[0] or 0
    
    # KPI 3: Productos agotados (Stock exactamente en 0)
    agotados = db.execute('SELECT COUNT(*) FROM productos WHERE cantidad = 0').fetchone()[0] or 0
    
    # KPI 4: Total unidades físicas (Suma de todo el inventario)
    total_unidades = db.execute('SELECT SUM(cantidad) FROM productos').fetchone()[0] or 0
    
    db.close()
    
    return render_template('index.html', 
                           productos=productos, 
                           movimientos=movimientos,
                           total_skus=total_skus,
                           bajo_stock=bajo_stock,
                           agotados=agotados,
                           total_unidades=total_unidades)

# --- BUSCA ESTA PARTE Y DÉJALA ASÍ ---

@app.route('/agregar', methods=['POST'])
@login_required
def agregar():  # <--- ANTES DECÍA exportar_reporte, CÁMBIALO A agregar
    nombre = request.form.get('nombre')
    cantidad = request.form.get('cantidad')
    stock_minimo = request.form.get('stock_minimo')
    
    db = conectar_db()
    try:
        # 1. Insertar el producto
        cursor = db.execute(
            'INSERT INTO productos (nombre, cantidad, stock_minimo) VALUES (?, ?, ?)',
            (nombre, cantidad, stock_minimo)
        )
        producto_id = cursor.lastrowid

        # 2. Registrar el movimiento
        db.execute(
            'INSERT INTO movimientos (producto_id, usuario_id, tipo, cantidad) VALUES (?, ?, ?, ?)',
            (producto_id, current_user.id, 'entrada', cantidad)
        )
        
        db.commit()
        return jsonify({
            'status': 'success',
            'nombre': nombre,
            'cantidad': cantidad
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        db.close()



@app.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    db = conectar_db()
    # Por seguridad e integridad, primero registramos que el stock sale o se elimina
    # (En sistemas avanzados, no se borra el producto, se desactiva, pero aquí lo borraremos)
    db.execute('DELETE FROM movimientos WHERE producto_id = ?', (id,))
    db.execute('DELETE FROM productos WHERE id = ?', (id,))
    db.commit()
    db.close()
    flash('Producto eliminado')
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
def exportar_reporte():  
    db = conectar_db()
    try:
        # Usamos 'fecha_creacion' porque así está en tu archivo crear_db.py
        query = """
            SELECT nombre, 
                   cantidad AS [Cantidad Actual], 
                   stock_minimo AS [Mínimo Permitido], 
                   fecha_creacion AS [Fecha de Ingreso]
            FROM productos
        """
        df = pd.read_sql_query(query, db)
        db.close()
        
        # Formatear la fecha para que sea legible (Día/Mes/Año)
        if not df.empty:
            df['Fecha de Ingreso'] = pd.to_datetime(df['Fecha de Ingreso']).dt.strftime('%d/%m/%Y %H:%M')

        # Creamos el archivo en memoria (más rápido y evita problemas de permisos en Windows)
        import io
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Inventario')
            # Auto-ajuste de columnas
            worksheet = writer.sheets['Inventario']
            for i, col in enumerate(df.columns):
                column_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, column_len)
        
        output.seek(0)
        
        return send_file(
            output, 
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True, 
            download_name='Reporte_StockPro_Inventario.xlsx'
        )
        
    except Exception as e:
        if 'db' in locals(): db.close()
        return f"Error al generar reporte: {str(e)}", 500