import sqlite3
from werkzeug.security import generate_password_hash

# Conexión a la base de datos SQLite
# conn = sqlite3.connect("../resources/db/trabajadores.db")
# TODO: Crear usuarios en Firebase, no en base de datos local.

# Crear la tabla si no existe
# cur.execute("""
#     CREATE TABLE IF NOT EXISTS trabajadores (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         username TEXT UNIQUE NOT NULL,
#         password TEXT NOT NULL
#     );
# """)

usuarios = [
    ("Thomas", generate_password_hash("1109")),
    ("Ricardo", generate_password_hash("1234")),
    ("Prueba", generate_password_hash("prueba123")),
    ("TestUser", generate_password_hash("testpass"))
]

for username, password in usuarios:
    try:
        # cur.execute(
        #     "INSERT INTO trabajadores (username, password) VALUES (?, ?)",
        #     (username, password)
        # )
        pass  # El usuario ya existe, no hacer nada
    except sqlite3.IntegrityError:
        pass  # El usuario ya existe, no hacer nada

# conn.commit()
# cur.close()
# conn.close()