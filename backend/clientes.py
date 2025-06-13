from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .servicios import leer_servicios, obtener_tareas_por_servicio
import requests
from datetime import datetime

clientes_bp = Blueprint('clientes', __name__)

FIREBASE_TRABAJOS_URL = "https://base-datos-rv-default-rtdb.firebaseio.com/trabajos.json"

@clientes_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    servicios_digitales = leer_servicios("digital")
    servicios_fisicos = leer_servicios("fisico")
    if request.method == "POST":
        nombre = request.form.get("nombre")
        cantidad = request.form.get("cantidad")
        servicio = request.form.get("servicio")
        tipo_servicio = request.form.get("tipo_servicio")
        observaciones = request.form.get("observaciones", "")
        fecha_de_solicitud = datetime.now().strftime("%d/%m/%Y")
        # Obtener los pasos/tareas del servicio seleccionado
        pasos = obtener_tareas_por_servicio(servicio, tipo_servicio)
        trabajo = {
            "nombre": nombre,
            "cantidad": cantidad,
            "servicio": servicio,
            "tipo_servicio": tipo_servicio,
            "observaciones": observaciones,
            "fecha_de_solicitud": fecha_de_solicitud,
            "progreso": 0,
            "pasos": pasos  # Guardar los pasos/tareas como parte del trabajo
        }
        try:
            resp = requests.post(FIREBASE_TRABAJOS_URL, json=trabajo)
            if resp.status_code == 200:
                flash("Trabajo registrado correctamente", "mensaje-success")
            else:
                flash(f"Error al registrar trabajo: {resp.status_code} {resp.text}", "mensaje-error")
        except Exception as e:
            flash(f"Error al conectar con Firebase: {e}", "mensaje-error")
        return redirect(url_for("clientes.index"))
    return render_template("index.html", servicios_digitales=servicios_digitales, servicios_fisicos=servicios_fisicos)

@clientes_bp.route("/usuarios")
@login_required
def mostrar_usuarios():
    trabajos = []
    try:
        resp = requests.get(FIREBASE_TRABAJOS_URL)
        if resp.status_code == 200 and resp.json():
            data = resp.json()
            # data es un dict con id aleatorio como clave
            for key, value in data.items():
                value["id"] = key
                trabajos.append(value)
            # Ordenar por fecha_de_solicitud (más reciente primero)
            trabajos.sort(key=lambda t: datetime.strptime(t.get("fecha_de_solicitud", "01/01/1970"), "%d/%m/%Y"), reverse=True)
    except Exception as e:
        flash(f"Error al obtener trabajos: {e}", "mensaje-error")
    return render_template("usuarios.html", usuarios=trabajos)

@clientes_bp.route("/progreso/<usuario_id>", methods=["GET", "POST"])
@login_required
def progreso(usuario_id):
    # Obtener el trabajo desde Firebase
    trabajo = {}
    try:
        resp = requests.get(f"https://base-datos-rv-default-rtdb.firebaseio.com/trabajos/{usuario_id}.json")
        if resp.status_code == 200 and resp.json():
            trabajo = resp.json()
            trabajo["id"] = usuario_id
    except Exception as e:
        flash(f"Error al obtener el trabajo: {e}", "mensaje-error")
        return redirect(url_for("clientes.mostrar_usuarios"))

    pasos = trabajo.get("pasos", [])
    # Si los pasos vienen como string, conviértelos a lista
    if isinstance(pasos, str):
        pasos = [p.strip() for p in pasos.split(",") if p.strip()]
    tareas_completadas = trabajo.get("tareas_completadas", [])
    if not isinstance(tareas_completadas, list):
        import json
        try:
            tareas_completadas = json.loads(tareas_completadas)
        except Exception:
            tareas_completadas = []

    if request.method == "POST":
        nuevas_tareas = request.form.getlist("tareas_completadas")
        progreso = int(len(nuevas_tareas) / len(pasos) * 100) if pasos else 0
        # Actualizar en Firebase
        update_data = {
            "tareas_completadas": nuevas_tareas,
            "progreso": progreso
        }
        try:
            requests.patch(f"https://base-datos-rv-default-rtdb.firebaseio.com/trabajos/{usuario_id}.json", json=update_data)
            flash("¡Progreso guardado con éxito!", "mensaje-success")
        except Exception as e:
            flash(f"Error al actualizar el progreso: {e}", "mensaje-error")
        return redirect(url_for("clientes.mostrar_usuarios"))

    return render_template(
        "progreso.html",
        trabajo=trabajo,
        pasos=pasos,
        tareas_completadas=tareas_completadas,
        progreso=trabajo.get("progreso", 0)
    )

@clientes_bp.route("/editar_observaciones/<usuario_id>", methods=["GET", "POST"])
@login_required
def editar_observaciones_usuario(usuario_id):
    usuario = None  # Aquí deberías obtener el usuario desde Firebase si lo necesitas
    if request.method == "POST":
        # Aquí deberías actualizar las observaciones en Firebase si lo necesitas
        flash("Observaciones actualizadas", "mensaje-success")
        return redirect(url_for("clientes.mostrar_usuarios"))
    return render_template("editar_observaciones.html", usuario=usuario)

def safe_json_loads(s):
    import json
    try:
        if s and s.strip():
            return json.loads(s)
    except Exception:
        pass
    return []