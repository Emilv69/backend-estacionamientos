
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'secret_key_super_segura'

# Simulación de base de datos
users = []  # Usuarios registrados
parkings = []  # Estacionamientos publicados
reservations = []  # Reservas realizadas

# Decorador para verificar token y obtener el usuario
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'message': 'Token es requerido'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = next((u for u in users if u['email'] == data['email']), None)
        except:
            return jsonify({'message': 'Token inválido'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# Ruta para registrar usuarios o arrendadores
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if any(u['email'] == data['email'] for u in users):
        return jsonify({'message': 'El usuario ya existe'}), 400
    hashed_pw = generate_password_hash(data['password'], method='sha256')
    user = {
        'email': data['email'],
        'password': hashed_pw,
        'role': data.get('role', 'user')  # 'user' o 'owner'
    }
    users.append(user)
    return jsonify({'message': 'Usuario registrado correctamente'})

# Ruta para login y generación de token
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = next((u for u in users if u['email'] == data['email']), None)
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'message': 'Credenciales inválidas'}), 401
    token = jwt.encode({
        'email': user['email'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    return jsonify({'token': token})

# Crear un nuevo estacionamiento (solo arrendadores)
@app.route('/api/parkings', methods=['POST'])
@token_required
def create_parking(current_user):
    if current_user['role'] != 'owner':
        return jsonify({'message': 'Solo los arrendadores pueden crear estacionamientos'}), 403
    data = request.json
    new_parking = {
        'id': len(parkings) + 1,
        'direccion': data['direccion'],
        'numero': data['numero'],
        'dueno': current_user['email'],
        'tarifa': data['tarifa'],
        'horario': data['horario'],
        'penalizacion': data['penalizacion'],
        'condiciones': data.get('condiciones', ''),
        'lat': data.get('lat'),
        'lng': data.get('lng')
    }
    parkings.append(new_parking)
    return jsonify(new_parking), 201

# Obtener todos los estacionamientos disponibles
@app.route('/api/parkings', methods=['GET'])
@token_required
def get_parkings(current_user):
    return jsonify(parkings)

# Editar un estacionamiento (solo dueño puede hacerlo)
@app.route('/api/parkings/<int:parking_id>', methods=['PUT'])
@token_required
def edit_parking(current_user, parking_id):
    parking = next((p for p in parkings if p['id'] == parking_id), None)
    if not parking:
        return jsonify({'message': 'Estacionamiento no encontrado'}), 404
    if parking['dueno'] != current_user['email']:
        return jsonify({'message': 'No autorizado para modificar este estacionamiento'}), 403
    data = request.json
    parking.update({
        'direccion': data['direccion'],
        'numero': data['numero'],
        'tarifa': data['tarifa'],
        'horario': data['horario'],
        'penalizacion': data['penalizacion'],
        'condiciones': data.get('condiciones', ''),
        'lat': data.get('lat'),
        'lng': data.get('lng')
    })
    return jsonify(parking)

# Eliminar un estacionamiento (solo dueño puede hacerlo)
@app.route('/api/parkings/<int:parking_id>', methods=['DELETE'])
@token_required
def delete_parking(current_user, parking_id):
    global parkings
    parking = next((p for p in parkings if p['id'] == parking_id), None)
    if not parking:
        return jsonify({'message': 'Estacionamiento no encontrado'}), 404
    if parking['dueno'] != current_user['email']:
        return jsonify({'message': 'No autorizado para eliminar este estacionamiento'}), 403
    parkings = [p for p in parkings if p['id'] != parking_id]
    return jsonify({'message': 'Estacionamiento eliminado'}), 200

if __name__ == '__main__':
    app.run(debug=True)
