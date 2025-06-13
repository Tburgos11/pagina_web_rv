import requests

firebase_url = "https://base-datos-rv-default-rtdb.firebaseio.com/usuarios.json"

usuarios = {
    "Thomas": {"password": "1108"},
    "Ricardo": {"password": "1234"},
    "Tania": {"password": "1234"}
}

response = requests.put(firebase_url, json=usuarios)
print(response.status_code, response.text)
