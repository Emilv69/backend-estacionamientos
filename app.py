
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt, datetime

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'tu_clave_secreta'

usuarios = []  # Lista temporal para usuarios

# Registro
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if any(u['email'] == data['email'] for u in usuarios):
        return jsonify({"error": "Usuario ya registrado"}), 400

    hashed_password = generate_password_hash(data['password'])
    nuevo_usuario = {
        "id": len(usuarios) + 1,
        "nombre": data['nombre'],
        "email": data['email'],
        "password": hashed_password,
        "rol": data.get('rol', 'usuario')
    }
    usuarios.append(nuevo_usuario)
    return jsonify({"message": "Usuario registrado exitosamente"}), 201

# Login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = next((u for u in usuarios if u['email'] == data['email']), None)
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({"error": "Credenciales inválidas"}), 401

    token = jwt.encode({
        'id': user['id'],
        'rol': user['rol'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=4)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({"token": token})

# Ruta protegida de ejemplo
@app.route('/api/perfil', methods=['GET'])
def perfil():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Token requerido"}), 401

    try:
        datos = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        user = next((u for u in usuarios if u['id'] == datos['id']), None)
        return jsonify({"nombre": user['nombre'], "email": user['email'], "rol": user['rol']})
    except Exception as e:
        return jsonify({"error": str(e)}), 401

if __name__ == '__main__':
    app.run(debug=True)
