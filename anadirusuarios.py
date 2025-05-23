import os
import psycopg2
from werkzeug.security import generate_password_hash

# Usar DATABASE_URL de las variables de entorno (ideal para Render y producción)
DATABASE_URL = os.environ.get("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Solo crear la tabla si no existe (NO la borres ni la recrees)
cur.execute("""
    CREATE TABLE IF NOT EXISTS trabajadores (
        id SERIAL PRIMARY KEY,
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
    cur.execute(
        "INSERT INTO trabajadores (username, password) VALUES (%s, %s) ON CONFLICT (username) DO NOTHING",
        (username, password)
    )

conn.commit()
cur.close()
conn.close()