import os
import sqlite3


# Cambia el path según la base de datos que quieras inicializar
DB_PROGRESO = os.path.join(os.path.dirname(__file__), '../resources/db/progreso.db')
DB_ARCHIVADOS = os.path.join(os.path.dirname(__file__), '../resources/db/archivados.db')
DB_USUARIOS = os.path.join(os.path.dirname(__file__), '../resources/db/trabajadores.db')  # <-- Añadido

def get_conn_archivados():
    return sqlite3.connect(DB_ARCHIVADOS)

def get_conn_usuarios():
    return sqlite3.connect(DB_USUARIOS)

def get_conn_progreso():
    return sqlite3.connect(DB_PROGRESO)

def init_db_progreso():
    """Crea la tabla trabajos_progreso si no existe."""
    with get_conn_progreso() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trabajos_progreso (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                tipo_servicio TEXT NOT NULL,
                servicio TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                progreso INTEGER DEFAULT 0,
                observaciones TEXT,
                fecha_de_solicitud TEXT NOT NULL,
                tareas_completadas TEXT
            );
        """)
        conn.commit()

def init_db_archivados():
    """Crea la tabla trabajos_archivados si no existe."""
    with get_conn_archivados() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trabajos_archivados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                tipo_servicio TEXT NOT NULL,
                servicio TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                estado TEXT NOT NULL,
                observaciones TEXT,
                fecha_de_solicitud TEXT NOT NULL,
                fecha_de_entrega TEXT NOT NULL
            );
        """)
        conn.commit()