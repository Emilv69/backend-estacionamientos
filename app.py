from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

app = Flask(__name__)
CORS(app)

# Simulaciones en memoria para usuarios y estacionamientos
usuarios = []
estacionamientos = []

# Función para buscar un usuario por su email
def buscar_usuario(email):
    return next((u for u in usuarios if u["email"] == email), None)

# Ruta para registrar un nuevo usuario (arrendador o cliente)
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if buscar_usuario(data["email"]):
        return jsonify({"error": "Usuario ya registrado"}), 400
    usuario = {
        "id": str(uuid.uuid4()),
        "email": data["email"],
        "password": generate_password_hash(data["password"]),
        "tipo": data["tipo"]  # "arrendador" o "cliente"
    }
    usuarios.append(usuario)
    return jsonify({"mensaje": "Usuario registrado correctamente"}), 201

# Ruta para login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    usuario = buscar_usuario(data["email"])
    if usuario and check_password_hash(usuario["password"], data["password"]):
        return jsonify({"mensaje": "Login exitoso", "usuario_id": usuario["id"], "tipo": usuario["tipo"]}), 200
    return jsonify({"error": "Credenciales inválidas"}), 401

# Ruta para agregar un estacionamiento (solo para arrendadores)
@app.route('/api/estacionamientos', methods=['POST'])
def agregar_estacionamiento():
    data = request.json
    arrendador_id = data.get("arrendador_id")
    usuario = next((u for u in usuarios if u["id"] == arrendador_id and u["tipo"] == "arrendador"), None)
    if not usuario:
        return jsonify({"error": "Solo arrendadores pueden registrar estacionamientos"}), 403

    nuevo = {
        "id": str(uuid.uuid4()),
        "direccion": data["direccion"],
        "numero": data["numero"],
        "tarifa": data["tarifa"],
        "horario": data["horario"],
        "penalizacion": data["penalizacion"],
        "condiciones": data["condiciones"],
        "lat": data["lat"],
        "lng": data["lng"],
        "arrendador_id": arrendador_id
    }
    estacionamientos.append(nuevo)
    return jsonify(nuevo), 201

# Ruta para obtener todos los estacionamientos disponibles
@app.route('/api/estacionamientos', methods=['GET'])
def listar_estacionamientos():
    return jsonify(estacionamientos)

# Ruta para eliminar un estacionamiento (solo el dueño puede)
@app.route('/api/estacionamientos/<id>', methods=['DELETE'])
def eliminar_estacionamiento(id):
    data = request.json
    arrendador_id = data.get("arrendador_id")
    global estacionamientos
    estacionamientos = [e for e in estacionamientos if not (e["id"] == id and e["arrendador_id"] == arrendador_id)]
    return jsonify({"mensaje": "Estacionamiento eliminado"}), 200

# Ruta para eliminar cuenta de usuario
@app.route('/api/usuarios/<usuario_id>', methods=['DELETE'])
def eliminar_usuario(usuario_id):
    global usuarios, estacionamientos
    usuarios = [u for u in usuarios if u["id"] != usuario_id]
    estacionamientos = [e for e in estacionamientos if e["arrendador_id"] != usuario_id]
    return jsonify({"mensaje": "Cuenta eliminada"}), 200

if __name__ == '__main__':
    app.run(debug=True)
