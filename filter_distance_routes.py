
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

# Filtro avanzado
@app.route('/api/parkings/filter', methods=['POST'])
def filter_parkings():
    filters = request.json
    results = parkings

    if 'direccion' in filters:
        results = [p for p in results if filters['direccion'].lower() in p['direccion'].lower()]
    if 'tarifa_max' in filters:
        results = [p for p in results if p['tarifa'] <= filters['tarifa_max']]
    if 'condiciones' in filters:
        results = [p for p in results if all(cond in p['condiciones'] for cond in filters['condiciones'])]

    return jsonify(results)

# Cálculo de distancia geográfica (haversine)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # radio de la tierra en km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# Estacionamientos más cercanos
@app.route('/api/parkings/nearby', methods=['POST'])
def get_nearby():
    data = request.json
    user_lat = data.get("lat")
    user_lng = data.get("lng")

    sorted_parkings = sorted(parkings, key=lambda p: haversine(user_lat, user_lng, p['lat'], p['lng']))
    return jsonify(sorted_parkings[:5])

if __name__ == "__main__":
    app.run(debug=True)
