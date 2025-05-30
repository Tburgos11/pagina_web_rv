from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .db_utils import get_conn_progreso
from .servicios import leer_servicios, obtener_tareas_por_servicio
import json
from datetime import datetime

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    servicios_digitales = leer_servicios("digital.txt")
    servicios_fisicos = leer_servicios("fisico.txt")
    if request.method == "POST":
        nombre = request.form.get("nombre")
        cantidad = request.form.get("cantidad")
        servicio = request.form.get("servicio")
        tipo_servicio = request.form.get("tipo_servicio")
        observaciones = request.form.get("observaciones", "")
        fecha_de_solicitud = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("Datos a guardar en la base de datos:")
        print("nombre:", nombre)
        print("cantidad:", cantidad)
        print("servicio:", servicio)
        print("tipo_servicio:", tipo_servicio)
        print("progreso:", 0)
        print("tareas_completadas:", "[]")
        print("observaciones:", observaciones)
        print("fecha_de_solicitud:", fecha_de_solicitud)
        with get_conn_progreso() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO trabajos_progreso (nombre, cantidad, servicio, tipo_servicio, progreso, observaciones, fecha_de_solicitud, tareas_completadas) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (nombre, cantidad, servicio, tipo_servicio, 0, observaciones, fecha_de_solicitud, "[]")
            )
            conn.commit()
        flash("Trabajo registrado correctamente", "mensaje-success")
        return redirect(url_for("clientes.index"))
    return render_template("index.html", servicios_digitales=servicios_digitales, servicios_fisicos=servicios_fisicos)

@clientes_bp.route("/usuarios")
@login_required
def mostrar_usuarios():
    with get_conn_progreso() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trabajos_progreso")
        trabajos = cursor.fetchall()
        print("----- DATOS MOSTRADOS EN LA TABLA DE USUARIOS -----")
        for fila in trabajos:
            print(f"Orden de columnas: id={fila[0]}, nombre={fila[1]}, tipo_servicio={fila[2]}, servicio={fila[3]}, cantidad={fila[4]}, progreso={fila[5]}, observaciones={fila[6]}, fecha_de_solicitud={fila[7]}, tareas_completadas={fila[8]}")
        print("---------------------------------------------------")
    return render_template("usuarios.html", usuarios=trabajos)

@clientes_bp.route("/progreso/<int:usuario_id>", methods=["GET", "POST"])
@login_required
def progreso(usuario_id):
    if request.method == "POST":
        # Obtener las tareas del servicio para calcular el progreso
        trabajo_actual = None
        with get_conn_progreso() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trabajos_progreso WHERE id = ?", (usuario_id,))
            fila = cursor.fetchone()
            if not fila:
                flash("No se encontró ningún registro con ese ID.", "mensaje-error")
                return redirect(url_for("clientes.mostrar_usuarios"))
            trabajo_actual = {
                "id": fila[0],
                "nombre": fila[1],
                "cantidad": fila[2],
                "servicio": fila[3],
                "tipo_servicio": fila[4],
                "progreso": fila[5],
                "tareas_completadas": fila[6],
                "observaciones": fila[7]
            }
        servicio = trabajo_actual["servicio"]
        tipo_servicio = trabajo_actual["tipo_servicio"]
        tareas = obtener_tareas_por_servicio(servicio, tipo_servicio)
        nuevas_tareas = request.form.getlist("tareas_completadas")
        progreso = int(len(nuevas_tareas) / len(tareas) * 100) if tareas else 0
        with get_conn_progreso() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE trabajos_progreso SET tareas_completadas = ?, progreso = ? WHERE id = ?",
                (json.dumps(nuevas_tareas), progreso, usuario_id)
            )
            conn.commit()
        flash("¡Progreso guardado con éxito!", "mensaje-success")
        return redirect(url_for("clientes.mostrar_usuarios"))

    # GET: Mostrar el progreso actual
    with get_conn_progreso() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trabajos_progreso WHERE id = ?", (usuario_id,))
        fila = cursor.fetchone()
        if not fila:
            flash("No se encontró ningún registro con ese ID.", "mensaje-error")
            return redirect(url_for("clientes.mostrar_usuarios"))
        trabajo = {
            "id": fila[0],
            "nombre": fila[1],
            "cantidad": fila[2],
            "servicio": fila[3],
            "tipo_servicio": fila[4],
            "progreso": fila[5],
            "tareas_completadas": fila[6],
            "observaciones": fila[7]
        }
    servicio = trabajo["servicio"]
    tipo_servicio = trabajo["tipo_servicio"]
    tareas = obtener_tareas_por_servicio(servicio, tipo_servicio)
    tareas_completadas = safe_json_loads(trabajo["tareas_completadas"])
    progreso = trabajo["progreso"]

    # Imprime toda la información relevante
    print("----- INFORMACIÓN AL ENTRAR A PROGRESO -----")
    print("Trabajo:", trabajo)
    print("Servicio:", servicio)
    print("Tipo de servicio:", tipo_servicio)
    print("Tareas:", tareas)
    print("Tareas completadas:", tareas_completadas)
    print("Progreso:", progreso)
    print("--------------------------------------------")

    return render_template(
        "progreso.html",
        trabajo=trabajo,
        tareas=tareas,
        tareas_completadas=tareas_completadas,
        progreso=progreso
    )

@clientes_bp.route("/editar_observaciones/<int:id>", methods=["GET", "POST"])
@login_required
def editar_observaciones_usuario(id):
    with get_conn_progreso() as conn:
        cursor = conn.cursor()
        if request.method == "POST":
            nuevas_observaciones = request.form.get("observaciones")
            cursor.execute("UPDATE trabajos_progreso SET observaciones = ? WHERE id = ?", (nuevas_observaciones, id))
            conn.commit()
            flash("Observaciones actualizadas", "mensaje-success")
            return redirect(url_for("clientes.mostrar_usuarios"))
        cursor.execute("SELECT * FROM trabajos_progreso WHERE id = ?", (id,))
        usuario = cursor.fetchone()
    return render_template("editar_observaciones.html", usuario=usuario)

def safe_json_loads(s):
    import json
    try:
        if s and s.strip():
            return json.loads(s)
    except Exception:
        pass
    return []