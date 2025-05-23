import os
import sqlite3
import json
import datetime
import csv

from flask import Flask, render_template, request, redirect, url_for, flash, send_file, Response
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = "clave_secreta"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

DATABASE_PATH = "trabajadores.db"

def get_conn():
    return sqlite3.connect(DATABASE_PATH)

# --- INICIALIZACIÓN DE TABLAS SI NO EXISTEN ---
def init_db():
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS datos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                cantidad INTEGER,
                servicio TEXT,
                progreso INTEGER,
                tareas_completadas TEXT,
                observaciones TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                cantidad INTEGER,
                servicio TEXT,
                estado TEXT,
                progreso INTEGER,
                observaciones TEXT,
                fecha_entrega TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trabajadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
        """)
        conn.commit()

TODAS_LAS_TAREAS = [
    "Revisión de documentos",
    "Llamada al cliente",
    "Entrega de producto",
    "Seguimiento post-venta"
]

def leer_servicios(nombre_archivo):
    ruta = os.path.join(os.path.dirname(__file__), nombre_archivo)
    with open(ruta, encoding="utf-8") as f:
        servicios = [line.strip() for line in f if line.strip()]
    return sorted(servicios, key=lambda s: s.lower())

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    servicios_digitales = leer_servicios("digital.txt")
    servicios_fisicos = leer_servicios("fisico.txt")
    if request.method == "POST":
        nombre = request.form.get("nombre")
        cantidad = request.form.get("cantidad")
        tipo_servicio = request.form.get("tipo_servicio")
        servicio = request.form.get("servicio")
        observaciones = request.form.get("observaciones", "")
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO datos (nombre, cantidad, servicio, progreso, tareas_completadas, observaciones) VALUES (?, ?, ?, ?, ?, ?)",
                (nombre, cantidad, servicio, 0, "[]", observaciones)
            )
            conn.commit()
        flash("¡Cliente guardado exitosamente!", "success")
        return redirect(url_for("index"))
    return render_template(
        "index.html",
        servicios_digitales=servicios_digitales,
        servicios_fisicos=servicios_fisicos
    )

@app.route("/usuarios")
@login_required
def mostrar_usuarios():
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM datos")
        usuarios = cursor.fetchall()
        usuarios_normalizados = []
        for usuario in usuarios:
            usuario = list(usuario)
            estado = usuario[4]
            # Traduce el estado a porcentaje
            if estado == "Completado":
                progreso = 100
            elif estado == "En Progreso":
                progreso = 50
            elif estado == "Pendiente":
                progreso = 0
            else:
                # Si tienes un campo progreso numérico, úsalo como respaldo
                try:
                    progreso = int(usuario[5]) if usuario[5] is not None else 0
                except Exception:
                    progreso = 0
            usuario[5] = progreso
            usuarios_normalizados.append(usuario)
    return render_template("usuarios.html", usuarios=usuarios_normalizados)

@app.route("/registros")
@login_required
def mostrar_registros():
    estado = request.args.get("estado", "")
    servicio = request.args.get("servicio", "")
    buscar = request.args.get("buscar", "")
    ordenar = request.args.get("ordenar", "id")
    direccion = request.args.get("direccion", "asc")
    fecha_inicio = request.args.get("fecha_inicio", "")
    fecha_fin = request.args.get("fecha_fin", "")

    query = "SELECT * FROM registros WHERE 1=1"
    params = []

    if estado:
        query += " AND estado = ?"
        params.append(estado)
    if servicio:
        query += " AND servicio = ?"
        params.append(servicio)
    if buscar:
        query += " AND nombre LIKE ?"
        params.append(f"%{buscar}%")
    if fecha_inicio:
        query += " AND fecha_entrega >= ?"
        params.append(fecha_inicio)
    if fecha_fin:
        query += " AND fecha_entrega <= ?"
        params.append(fecha_fin)

    columnas_validas = ["id", "nombre", "cantidad", "servicio", "estado", "progreso", "fecha_entrega"]
    if ordenar not in columnas_validas:
        ordenar = "id"
    if direccion not in ["asc", "desc"]:
        direccion = "asc"

    query += f" ORDER BY {ordenar} {direccion}"

    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        registros = cursor.fetchall()
        cursor.execute("SELECT DISTINCT estado FROM registros")
        estados = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT servicio FROM registros")
        servicios = [row[0] for row in cursor.fetchall()]

    return render_template(
        "registros.html",
        registros=registros,
        estados=estados,
        servicios=servicios,
        estado_actual=estado,
        servicio_actual=servicio,
        buscar_actual=buscar,
        ordenar_actual=ordenar,
        direccion_actual=direccion,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )

@app.route('/editar_observaciones/<int:id>', methods=['GET', 'POST'])
def editar_observaciones(id):
    if request.method == 'POST':
        nuevas_observaciones = request.form['observaciones']
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE registros SET observaciones = ? WHERE id = ?", (nuevas_observaciones, id))
            conn.commit()
        return redirect(url_for('mostrar_registros'))

    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT observaciones FROM registros WHERE id = ?", (id,))
        observacion = cursor.fetchone()
        observacion = observacion[0] if observacion else ''
    return render_template('editar_observaciones.html', id=id, observacion=observacion)

@app.route('/editar_observaciones_usuario/<int:id>', methods=['POST'])
@login_required
def editar_observaciones_usuario(id):
    nuevas_observaciones = request.form['observaciones']
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE datos SET observaciones = ? WHERE id = ?", (nuevas_observaciones, id))
        conn.commit()
    flash("Observaciones actualizadas correctamente.", "success")
    return redirect(url_for('mostrar_usuarios'))

@app.route('/mover_a_registros/<int:id>')
def mover_a_registros(id):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM datos WHERE id = ?", (id,))
        proyecto = cursor.fetchone()
        if proyecto:
            cursor.execute("""
                INSERT INTO registros (nombre, cantidad, servicio, estado, progreso, observaciones)
                VALUES (?, ?, ?, ?, ?, ?)
            """, proyecto[1:7])  # saltamos el id (proyecto[0])
            cursor.execute("DELETE FROM datos WHERE id = ?", (id,))
            conn.commit()
    return redirect(url_for('mostrar_usuarios'))

@app.route('/progreso/<int:usuario_id>', methods=['GET', 'POST'])
@login_required
def progreso(usuario_id):
    if request.method == 'POST':
        accion = request.form.get('accion')
        if accion == 'cancelar':
            with get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nombre, cantidad, servicio, observaciones FROM datos WHERE id = ?", (usuario_id,))
                usuario = cursor.fetchone()
                if usuario:
                    cursor.execute("""
                        INSERT INTO registros (nombre, cantidad, servicio, estado, observaciones)
                        VALUES (?, ?, ?, ?, ?)
                    """, (usuario[0], usuario[1], usuario[2], "Cancelado", usuario[3]))
                    cursor.execute("DELETE FROM datos WHERE id = ?", (usuario_id,))
                    conn.commit()
            return redirect(url_for('mostrar_registros'))

        tareas_completadas = request.form.getlist('tarea')
        progreso = int((len(tareas_completadas) / len(TODAS_LAS_TAREAS)) * 100) if TODAS_LAS_TAREAS else 0

        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE datos SET progreso = ?, tareas_completadas = ? WHERE id = ?",
                (progreso, json.dumps(tareas_completadas), usuario_id)
            )
            if progreso == 100:
                cursor.execute("SELECT nombre, cantidad, servicio, observaciones FROM datos WHERE id = ?", (usuario_id,))
                usuario = cursor.fetchone()
                if usuario:
                    fecha_entrega = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute("""
                        INSERT INTO registros (nombre, cantidad, servicio, estado, observaciones, fecha_entrega)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (usuario[0], usuario[1], usuario[2], "Completado", usuario[3], fecha_entrega))
                    cursor.execute("DELETE FROM datos WHERE id = ?", (usuario_id,))
                conn.commit()
                return redirect(url_for('mostrar_registros'))
            else:
                conn.commit()
                return redirect(url_for('mostrar_usuarios'))

    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT progreso, tareas_completadas FROM datos WHERE id = ?", (usuario_id,))
        row = cursor.fetchone()
        progreso_actual = row[0] if row else 0
        tareas_completadas = json.loads(row[1]) if row and row[1] else []

    return render_template(
        "progreso.html",
        tareas=TODAS_LAS_TAREAS,
        progreso=progreso_actual,
        tareas_completadas=tareas_completadas,
        usuario_id=usuario_id
    )

class Trabajador(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password FROM trabajadores WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if user:
            return Trabajador(*user)
    return None

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password FROM trabajadores WHERE username = ?", (username,))
            user = cursor.fetchone()
            if user and check_password_hash(user[2], password):
                login_user(Trabajador(*user))
                return redirect(url_for("index"))
            else:
                flash("Usuario o contraseña incorrectos")
    return render_template("login.html")

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    if request.method == "POST":
        return '', 204
    return redirect(url_for("login"))

@app.route('/nuevo_usuario', methods=['POST'])
def nuevo_usuario():
    # Lógica para guardar el usuario
    # ...
    flash('¡Usuario guardado exitosamente!', 'success')
    return redirect(url_for('ruta_donde_redirigir'))

@app.route('/guardar_cliente', methods=['POST'])
def guardar_cliente():
    # Lógica para guardar el cliente
    # ...
    flash('¡Cliente guardado exitosamente!', 'success')
    return redirect(url_for('progreso'))

@app.route('/descargar_db')
@login_required
def descargar_db():
    return send_file('database.db', as_attachment=True)

@app.route('/descargar_registros_csv')
@login_required
def descargar_registros_csv():
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM registros")
        rows = cursor.fetchall()
        headers = [description[0] for description in cursor.description]

    def generate():
        data = [headers] + list(rows)
        for row in data:
            yield ','.join(map(str, row)) + '\n'

    return Response(generate(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=registros.csv"})


if __name__ == "__main__":
    init_db()  # Asegura que las tablas existen antes de correr la app
    app.run(host="0.0.0.0", port=5000, debug=True)