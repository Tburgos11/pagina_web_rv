import os
import sqlite3
from datetime import datetime


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

def archivar_trabajo(id_trabajo, estado="Completado"):
    # 1. Obtener el registro de progreso
    with get_conn_progreso() as conn_prog:
        cursor = conn_prog.cursor()
        cursor.execute("""
            SELECT id, nombre, tipo_servicio, servicio, cantidad, observaciones, fecha_de_solicitud, tareas_completadas
            FROM trabajos_progreso WHERE id = ?
        """, (id_trabajo,))
        trabajo = cursor.fetchone()
        if not trabajo:
            return False  # No existe

    # 2. Preparar datos para archivados
    fecha_de_entrega = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    datos_archivados = (
        trabajo[1],  # nombre
        trabajo[2],  # tipo_servicio
        trabajo[3],  # servicio
        trabajo[4],  # cantidad
        estado,      # estado
        trabajo[5],  # observaciones
        trabajo[6],  # fecha_de_solicitud
        fecha_de_entrega  # fecha_de_entrega
    )

    print("Datos que se insertan en trabajos_archivados:", datos_archivados)  # <-- Agregado

    # 3. Insertar en archivados
    with get_conn_archivados() as conn_arch:
        cursor_arch = conn_arch.cursor()
        cursor_arch.execute("""
            INSERT INTO trabajos_archivados
            (nombre, tipo_servicio, servicio, cantidad, estado, observaciones, fecha_de_solicitud, fecha_de_entrega)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, datos_archivados)
        conn_arch.commit()

    # 4. Eliminar de progreso
    with get_conn_progreso() as conn_prog:
        cursor = conn_prog.cursor()
        cursor.execute("DELETE FROM trabajos_progreso WHERE id = ?", (id_trabajo,))
        conn_prog.commit()

    return True