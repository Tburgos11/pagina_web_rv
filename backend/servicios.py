import os

def leer_servicios(nombre_archivo):
    ruta = os.path.join(os.path.dirname(__file__), f'../resources/{nombre_archivo}')
    with open(ruta, encoding="utf-8") as f:
        servicios = []
        for line in f:
            line = line.strip()
            if line:
                nombre_servicio = line.split(',')[0]
                servicios.append(nombre_servicio)
    return sorted(servicios, key=lambda s: s.lower())

def obtener_tareas_por_servicio(servicio, tipo_servicio):
    archivo = "digital.txt" if tipo_servicio == "digital" else "fisico.txt"
    ruta = os.path.join(os.path.dirname(__file__), f'../resources/{archivo}')
    servicio_str = str(servicio).strip().lower()
    with open(ruta, encoding="utf-8") as f:
        for line in f:
            partes = line.strip().split(',')
            if partes and partes[0].strip().lower() == servicio_str:
                tareas = [p.strip() for p in partes[1:]]
                return tareas
    return []