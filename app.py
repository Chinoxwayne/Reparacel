from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2 # Cambiamos sqlite3 por psycopg2
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "reparacel_cloud_key"

# --- TU ENLACE DE SUPABASE ---
# REEMPLAZA [YOUR-PASSWORD] con tu contraseña real
DB_URL = "postgresql://postgres:[Aroldimaria1996]@db.xvavvwozkbietoiyyqql.supabase.co:5432/postgres"

def conectar():
    return psycopg2.connect(DB_URL)

def crear_tablas_nube():
    conn = conectar()
    cur = conn.cursor()
    # En PostgreSQL el autoincremento se llama SERIAL
    cur.execute('''CREATE TABLE IF NOT EXISTS inventario (
        id SERIAL PRIMARY KEY,
        nombre TEXT UNIQUE,
        cantidad INTEGER,
        costo REAL,
        precio REAL
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS gastos (
        id SERIAL PRIMARY KEY,
        descripcion TEXT,
        monto REAL,
        fecha TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS factura (
        id SERIAL PRIMARY KEY,
        cliente TEXT,
        fecha TEXT,
        total REAL
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS factura_detalle (
        id SERIAL PRIMARY KEY,
        factura_id INTEGER,
        servicio TEXT,
        cantidad INTEGER,
        precio_unitario REAL,
        subtotal REAL
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS servicios (
        id SERIAL PRIMARY KEY,
        nombre TEXT,
        precio REAL
    )''')
    conn.commit()
    cur.close()
    conn.close()

# Inicializar tablas en la nube
crear_tablas_nube()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inventario')
def ver_inventario():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT nombre, cantidad, costo, precio FROM inventario ORDER BY nombre ASC")
    productos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('inventario.html', productos=productos, moneda="RD$")

@app.route('/gastos', methods=['GET', 'POST'])
def gestionar_gastos():
    conn = conectar()
    cur = conn.cursor()
    if request.method == 'POST':
        desc = request.form.get('descripcion').upper()
        monto = request.form.get('monto')
        fecha = datetime.now().strftime("%d/%m/%Y")
        cur.execute("INSERT INTO gastos (descripcion, monto, fecha) VALUES (%s, %s, %s)", (desc, monto, fecha))
        conn.commit()
        return redirect(url_for('gestionar_gastos'))
    
    cur.execute("SELECT * FROM gastos ORDER BY id DESC LIMIT 10")
    gastos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('gastos.html', gastos=gastos, moneda="RD$")

# ... (Aquí irían las demás rutas de facturar y balance con el mismo formato %s)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)