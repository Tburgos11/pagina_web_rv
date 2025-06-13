import os
from flask import Flask, render_template
from backend.clientes import clientes_bp
from backend.auth import auth_bp, init_login_manager
from backend.registros import registros_bp
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '../templates'),
    static_folder=os.path.join(os.path.dirname(__file__), '../static')
)
app.secret_key = "clave_secreta"

app.register_blueprint(clientes_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(registros_bp)

init_login_manager(app)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, port=5001)