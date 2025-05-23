import sqlite3
from werkzeug.security import generate_password_hash

usuarios = [
    ("Thomas", generate_password_hash("1109")),
    ("Ricardo", generate_password_hash("1234")),
    ("Prueba", generate_password_hash("prueba123"))  # Usuario de prueba añadido
]

conn = sqlite3.connect("trabajadores.db")
for username, password in usuarios:
    try:
        conn.execute("INSERT INTO trabajadores (username, password) VALUES (?, ?)", (username, password))
    except sqlite3.IntegrityError:
        print(f"El usuario {username} ya existe.")
conn.commit()
conn.close()

conn = sqlite3.connect("registros.db")
conn.execute("ALTER TABLE registros ADD COLUMN fecha_entrega TEXT")
conn.commit()
conn.close()