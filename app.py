from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

parkings = [
    {
        "id": 1,
        "direccion": "Av. Providencia 1234",
        "numero": "E-21",
        "dueno": "Juan Pérez",
        "tarifa": 2000,
        "horario": "Lun a Vie, 8:00 a 20:00",
        "penalizacion": 5000
    },
    {
        "id": 2,
        "direccion": "Los Leones 456",
        "numero": "B-15",
        "dueno": "María Gómez",
        "tarifa": 1800,
        "horario": "Lun a Dom, 7:00 a 22:00",
        "penalizacion": 4000
    }
]

@app.route('/api/parkings', methods=['GET'])
def get_parkings():
    return jsonify(parkings)

@app.route('/api/parkings', methods=['POST'])
def add_parking():
    data = request.json
    data["id"] = len(parkings) + 1
    parkings.append(data)
    return jsonify(data), 201

if __name__ == '__main__':
    app.run(debug=True)