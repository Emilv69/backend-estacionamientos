
from flask import Flask, request, jsonify
from flask_cors import CORS
import math

app = Flask(__name__)
CORS(app)

# Datos simulados de estacionamientos con coordenadas
parkings = [
    {
        "id": 1,
        "direccion": "Av. Providencia 1234",
        "numero": "E-21",
        "dueno": "Juan Pérez",
        "tarifa": 2000,
        "horario": "Lun a Vie, 8:00 a 20:00",
        "penalizacion": 5000,
        "condiciones": ["techado", "seguridad"],
        "lat": -33.42628,
        "lng": -70.6176
    },
    {
        "id": 2,
        "direccion": "Los Leones 456",
        "numero": "B-15",
        "dueno": "María Gómez",
        "tarifa": 1800,
        "horario": "Lun a Dom, 7:00 a 22:00",
        "penalizacion": 4000,
        "condiciones": ["24hrs"],
        "lat": -33.4177,
        "lng": -70.6082
    }
]

# Calcular distancia usando fórmula de Haversine
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# Nueva ruta para filtrar y ordenar estacionamientos por criterios y distancia
@app.route('/api/parkings/filter', methods=['POST'])
def filter_parkings():
    filters = request.json
    results = parkings

    if 'direccion' in filters:
        results = [p for p in results if filters['direccion'].lower() in p['direccion'].lower()]
    if 'tarifa_max' in filters:
        results = [p for p in results if p['tarifa'] <= filters['tarifa_max']]
    if 'condiciones' in filters:
        for cond in filters['condiciones']:
            results = [p for p in results if cond in p.get('condiciones', [])]
    if 'lat' in filters and 'lng' in filters:
        user_lat, user_lng = filters['lat'], filters['lng']
        results.sort(key=lambda p: haversine(user_lat, user_lng, p['lat'], p['lng']))

    return jsonify(results)
