from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from .db_utils import get_conn_usuarios

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
        with get_conn_usuarios() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password FROM trabajadores WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return User(*row)
        return None

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        with get_conn_usuarios() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password FROM trabajadores WHERE username = ?", (username,))
            user = cursor.fetchone()
            if user and check_password_hash(user[2], password):
                user_obj = User(*user)
                login_user(user_obj)
                return redirect(url_for("clientes.index"))
            else:
                flash("Usuario o contraseña incorrectos", "mensaje-error")
    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))