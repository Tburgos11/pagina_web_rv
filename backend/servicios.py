import requests

FIREBASE_SERVICIOS_URL = "https://base-datos-rv-default-rtdb.firebaseio.com/servicios"

def leer_servicios(tipo_servicio):
    """
    Lee los servicios desde Firebase según el tipo ('digital' o 'fisico').
    Devuelve una lista de nombres de servicios.
    """
    url = f"{FIREBASE_SERVICIOS_URL}/{tipo_servicio}.json"
    resp = requests.get(url)
    servicios = []
    if resp.status_code == 200 and resp.json():
        data = resp.json()
        for key, value in data.items():
            # value puede ser un dict con nombre y pasos, o solo nombre
            if isinstance(value, dict) and "nombre" in value:
                servicios.append(value["nombre"])
            elif isinstance(value, str):
                servicios.append(value)
            else:
                servicios.append(key)
    return sorted(servicios, key=lambda s: s.lower())

def obtener_tareas_por_servicio(servicio, tipo_servicio):
    """
    Obtiene los pasos/tareas de un servicio desde Firebase.
    """
    url = f"{FIREBASE_SERVICIOS_URL}/{tipo_servicio}.json"
    resp = requests.get(url)
    if resp.status_code == 200 and resp.json():
        data = resp.json()
        for key, value in data.items():
            nombre = value["nombre"] if isinstance(value, dict) and "nombre" in value else key
            if nombre.strip().lower() == str(servicio).strip().lower():
                # Si los pasos están como string separados por coma
                if isinstance(value, dict) and "pasos" in value:
                    pasos = value["pasos"]
                    if isinstance(pasos, str):
                        return [p.strip() for p in pasos.split(",") if p.strip()]
                    elif isinstance(pasos, list):
                        return pasos
                elif isinstance(value, dict):
                    # Si los pasos están como otros campos en el dict
                    return [v for k, v in value.items() if k != "nombre"]
    return []