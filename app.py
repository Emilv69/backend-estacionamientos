
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
CORS(app)

# Clave secreta para codificar el token JWT
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'

# Bases de datos simuladas en memoria
users = []  # Lista de usuarios registrados
parkings = []  # Lista de estacionamientos publicados

# Decorador para requerir autenticación con JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            bearer = request.headers['Authorization']
            if bearer.startswith('Bearer '):
                token = bearer[7:]
        if not token:
            return jsonify({'message': 'Token es requerido'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = next((u for u in users if u['username'] == data['username']), None)
        except:
            return jsonify({'message': 'Token inválido'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# Ruta para registrar usuario (user o owner)
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if next((u for u in users if u['username'] == data['username']), None):
        return jsonify({'message': 'Usuario ya existe'}), 400
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = {
        'username': data['username'],
        'password': hashed_password,
        'role': data.get('role', 'user')  # Puede ser 'user' o 'owner'
    }
    users.append(new_user)
    return jsonify({'message': 'Usuario registrado exitosamente'}), 201

# Ruta para iniciar sesión
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = next((u for u in users if u['username'] == data['username']), None)
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'message': 'Credenciales inválidas'}), 401
    token = jwt.encode({
        'username': user['username'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    return jsonify({'token': token})

# Ruta para crear un nuevo estacionamiento (solo arrendadores)
@app.route('/api/parkings', methods=['POST'])
@token_required
def create_parking(current_user):
    if current_user['role'] != 'owner':
        return jsonify({'message': 'Solo los arrendadores pueden crear estacionamientos'}), 403
    data = request.get_json()
    data['id'] = len(parkings) + 1
    data['owner'] = current_user['username']
    parkings.append(data)
    return jsonify({'message': 'Estacionamiento creado', 'parking': data}), 201

# Ruta para ver todos los estacionamientos (usuarios autenticados)
@app.route('/api/parkings', methods=['GET'])
@token_required
def list_parkings(current_user):
    return jsonify(parkings)

# Ruta para editar un estacionamiento (solo su dueño)
@app.route('/api/parkings/<int:parking_id>', methods=['PUT'])
@token_required
def update_parking(current_user, parking_id):
    parking = next((p for p in parkings if p['id'] == parking_id and p['owner'] == current_user['username']), None)
    if not parking:
        return jsonify({'message': 'Estacionamiento no encontrado o acceso denegado'}), 404
    data = request.get_json()
    parking.update(data)
    return jsonify({'message': 'Estacionamiento actualizado', 'parking': parking})

# Ruta para eliminar un estacionamiento (solo su dueño)
@app.route('/api/parkings/<int:parking_id>', methods=['DELETE'])
@token_required
def delete_parking(current_user, parking_id):
    global parkings
    parkings = [p for p in parkings if not (p['id'] == parking_id and p['owner'] == current_user['username'])]
    return jsonify({'message': 'Estacionamiento eliminado si existía'})

# Ruta para eliminar cuenta de usuario
@app.route('/api/delete_account', methods=['DELETE'])
@token_required
def delete_account(current_user):
    global users, parkings
    users = [u for u in users if u['username'] != current_user['username']]
    if current_user['role'] == 'owner':
        parkings = [p for p in parkings if p['owner'] != current_user['username']]
    return jsonify({'message': 'Cuenta eliminada'})

# Ruta raíz
@app.route('/')
def index():
    return 'API de Estacionamientos funcionando correctamente'

if __name__ == '__main__':
    app.run(debug=True)
