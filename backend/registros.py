from flask import Blueprint, request, redirect, url_for, flash, render_template
import requests

registros_bp = Blueprint('registros', __name__)

FIREBASE_TRABAJOS_URL = "https://base-datos-rv-default-rtdb.firebaseio.com/trabajos.json"

@registros_bp.route("/registros")
def mostrar_registros():
    registros = []
    try:
        resp = requests.get(FIREBASE_TRABAJOS_URL)
        if resp.status_code == 200 and resp.json():
            data = resp.json()
            for key, value in data.items():
                value["id"] = key
                registros.append(value)
            registros.sort(key=lambda t: t.get("fecha_de_solicitud", ""), reverse=True)
    except Exception as e:
        flash(f"Error al obtener registros: {e}", "mensaje-error")
    return render_template("registros.html", registros=registros)