from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import json

app = Flask(__name__)

# Inicializar bases de datos y tablas
def init_db():
    with sqlite3.connect("database.db") as conn:
        # Tabla principal con datos activos
        conn.execute("""
            CREATE TABLE IF NOT EXISTS datos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                cantidad INTEGER,
                servicio TEXT,
                estado TEXT,
                progreso INTEGER,
                observaciones TEXT,
                tareas_completadas TEXT
            );
        """)
        # Tabla para registros archivados (finalizados o cancelados)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS registros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                cantidad INTEGER,
                servicio TEXT,
                estado TEXT,
                progreso INTEGER,
                observaciones TEXT
            );
        """)

def init_registros_db():
    with sqlite3.connect("registros.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS registros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                cantidad INTEGER,
                servicio TEXT,
                estado TEXT,
                progreso INTEGER,
                observaciones TEXT
            );
        """)

TODAS_LAS_TAREAS = [
    "Revisión de documentos",
    "Llamada al cliente",
    "Entrega de producto",
    "Seguimiento post-venta"
]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nombre = request.form["nombre"]
        cantidad = request.form["cantidad"]
        servicio = request.form["servicio"]
        # Inicialmente estado será 'En Progreso' y progreso 0
        estado = "En Progreso"
        progreso = 0
        observaciones = ""
        tareas_completadas = json.dumps([])
        with sqlite3.connect("database.db") as conn:
            conn.execute("INSERT INTO datos (nombre, cantidad, servicio, estado, progreso, observaciones, tareas_completadas) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (nombre, cantidad, servicio, estado, progreso, observaciones, tareas_completadas))
        return redirect("/")
    # Aquí deberías cargar los servicios para el select, por ahora lo dejaremos estático
    servicios = ["Servicio A", "Servicio B", "Servicio C"]
    return render_template("index.html", servicios=servicios)

@app.route("/usuarios")
def mostrar_usuarios():
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM datos")
        usuarios = cursor.fetchall()
        # Normalizar el campo progreso para cada usuario
        usuarios_normalizados = []
        for usuario in usuarios:
            usuario = list(usuario)
            try:
                progreso = int(usuario[5]) if usuario[5] is not None else 0
            except Exception:
                progreso = 0
            progreso = max(0, min(progreso, 100))
            usuario[5] = progreso
            usuarios_normalizados.append(usuario)
    return render_template("usuarios.html", usuarios=usuarios_normalizados)

@app.route("/registros")
def mostrar_registros():
    with sqlite3.connect("registros.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM registros")
        registros = cursor.fetchall()
    return render_template("registros.html", registros=registros)

@app.route('/editar_observaciones/<int:id>', methods=['GET', 'POST'])
def editar_observaciones(id):
    if request.method == 'POST':
        nuevas_observaciones = request.form['observaciones']
        with sqlite3.connect("database.db") as conn:
            conn.execute("UPDATE registros SET observaciones = ? WHERE id = ?", (nuevas_observaciones, id))
        return redirect(url_for('mostrar_registros'))

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT observaciones FROM registros WHERE id = ?", (id,))
        observacion = cursor.fetchone()
        observacion = observacion[0] if observacion else ''
    return render_template('editar_observaciones.html', id=id, observacion=observacion)

# Ruta para mover proyectos finalizados o cancelados a registros
@app.route('/mover_a_registros/<int:id>')
def mover_a_registros(id):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM datos WHERE id = ?", (id,))
        proyecto = cursor.fetchone()
        if proyecto:
            # Insertar en registros
            conn.execute("""
                INSERT INTO registros (nombre, cantidad, servicio, estado, progreso, observaciones)
                VALUES (?, ?, ?, ?, ?, ?)
            """, proyecto[1:])  # saltamos el id (proyecto[0])
            # Borrar de datos
            conn.execute("DELETE FROM datos WHERE id = ?", (id,))
    return redirect(url_for('mostrar_usuarios'))

@app.route('/progreso/<int:usuario_id>', methods=['GET', 'POST'])
def progreso(usuario_id):
    TODAS_LAS_TAREAS = [
        "Revisión de documentos",
        "Llamada al cliente",
        "Entrega de producto",
        "Seguimiento post-venta"
    ]

    if request.method == 'POST':
        accion = request.form.get('accion')
        if accion == 'cancelar':
            # Mover a registros.db con estado "Cancelado"
            with sqlite3.connect("database.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nombre, cantidad, servicio, observaciones FROM datos WHERE id = ?", (usuario_id,))
                usuario = cursor.fetchone()
                if usuario:
                    with sqlite3.connect("registros.db") as conn_reg:
                        conn_reg.execute("""
                            INSERT INTO registros (nombre, cantidad, servicio, estado, observaciones)
                            VALUES (?, ?, ?, ?, ?)
                        """, (usuario[0], usuario[1], usuario[2], "Cancelado", usuario[3]))
                    cursor.execute("DELETE FROM datos WHERE id = ?", (usuario_id,))
                conn.commit()
            return redirect(url_for('mostrar_registros'))

        # Acción normal de guardar progreso
        tareas_completadas = request.form.getlist('tarea')
        progreso = int((len(tareas_completadas) / len(TODAS_LAS_TAREAS)) * 100) if TODAS_LAS_TAREAS else 0

        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE datos SET progreso = ?, tareas_completadas = ? WHERE id = ?",
                (progreso, json.dumps(tareas_completadas), usuario_id)
            )
            if progreso == 100:
                cursor.execute("SELECT nombre, cantidad, servicio, observaciones FROM datos WHERE id = ?", (usuario_id,))
                usuario = cursor.fetchone()
                if usuario:
                    with sqlite3.connect("registros.db") as conn_reg:
                        conn_reg.execute("""
                            INSERT INTO registros (nombre, cantidad, servicio, estado, observaciones)
                            VALUES (?, ?, ?, ?, ?)
                        """, (usuario[0], usuario[1], usuario[2], "Completado", usuario[3]))
                    cursor.execute("DELETE FROM datos WHERE id = ?", (usuario_id,))
                conn.commit()
            return redirect(url_for('mostrar_registros'))

    with sqlite3.connect("database.db") as conn:
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

if __name__ == "__main__":
    init_db()
    init_registros_db()
    app.run(host="0.0.0.0", port=5000, debug=True)