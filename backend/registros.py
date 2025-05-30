from flask import Blueprint, render_template
from flask_login import login_required
from .db_utils import get_conn_archivados

registros_bp = Blueprint('registros', __name__)

@registros_bp.route("/registros")
@login_required
def mostrar_registros():
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM registros")
        registros = cursor.fetchall()
    return render_template("registros.html", registros=registros)