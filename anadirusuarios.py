import sqlite3
import os
from werkzeug.security import generate_password_hash

# Eliminar las bases de datos si existen
if os.path.exists("trabajadores.db"):
    os.remove("trabajadores.db")
if os.path.exists("registros.db"):
    os.remove("registros.db")

# Crear nueva base de datos de trabajadores y tabla
conn = sqlite3.connect("trabajadores.db")
conn.execute("""
    CREATE TABLE trabajadores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );
""")
usuarios = [
    ("Thomas", generate_password_hash("1109")),
    ("Ricardo", generate_password_hash("1234")),
    ("Prueba", generate_password_hash("prueba123")),
    ("TestUser", generate_password_hash("testpass"))
]
for username, password in usuarios:
    conn.execute("INSERT INTO trabajadores (username, password) VALUES (?, ?)", (username, password))
conn.commit()
conn.close()

# Crear nueva base de datos de registros y tabla
conn = sqlite3.connect("registros.db")
conn.execute("""
    CREATE TABLE registros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        cantidad INTEGER,
        servicio TEXT,
        estado TEXT,
        observaciones TEXT,
        fecha_entrega TEXT
    );
""")
conn.commit()
conn.close()