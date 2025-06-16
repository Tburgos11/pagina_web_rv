from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import requests

auth_bp = Blueprint('auth', __name__)

class User(UserMixin):
    def __init__(self, id_, username, password):
        self.id = id_
        self.username = username
        self.password = password

def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        try:
            resp = requests.get(FIREBASE_USERS_URL)
            if resp.status_code == 200:
                usuarios = resp.json()
                if usuarios and user_id in usuarios:
                    return User(id_=user_id, username=user_id, password=usuarios[user_id]["password"])
        except Exception as e:
            print("Error en load_user:", e)
        return None

FIREBASE_USERS_URL = "https://base-datos-rv-default-rtdb.firebaseio.com/usuarios.json"

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        try:
            resp = requests.get(FIREBASE_USERS_URL)
            if resp.status_code == 200:
                usuarios = resp.json()
                if usuarios and username in usuarios:
                    if usuarios[username]["password"] == password:
                        user = User(id_=username, username=username, password=password)
                        login_user(user)
                        flash("Inicio de sesión exitoso", "mensaje-exito")
                        return redirect(url_for("index"))
                flash("Usuario o contraseña incorrectos", "mensaje-error")
            else:
                flash(f"Error Firebase: {resp.status_code} {resp.text}", "mensaje-error")
        except Exception as e:
            flash(f"Error al conectar con la base de datos: {e}", "mensaje-error")
    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))