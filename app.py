
# ========== Código Base de la Aplicación ==========

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


# ========== Módulo: Recuperación de Contraseña ==========

from flask import Flask, request, jsonify
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message

app = Flask(__name__)

# Configuración del correo electrónico (ajustar con tus datos reales)
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'tu_correo@example.com'
app.config['MAIL_PASSWORD'] = 'tu_contraseña'
app.config['MAIL_DEFAULT_SENDER'] = 'tu_correo@example.com'

mail = Mail(app)
serializer = URLSafeTimedSerializer('CLAVE_SECRETA')

# Simulamos base de datos de usuarios
usuarios = {'usuario@example.com': {'password': '1234'}}

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    if email not in usuarios:
        return jsonify({'message': 'Correo no registrado'}), 404

    token = serializer.dumps(email, salt='reset-password')
    reset_link = f"http://localhost:3000/reset-password/{token}"

    msg = Message("Recuperación de contraseña", recipients=[email])
    msg.body = f"Usa este enlace para restablecer tu contraseña: {reset_link}"
    mail.send(msg)

    return jsonify({'message': 'Correo enviado con el enlace de recuperación'})

@app.route('/api/reset-password/<token>', methods=['POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='reset-password', max_age=3600)
    except Exception as e:
        return jsonify({'message': 'Token inválido o expirado'}), 400

    data = request.get_json()
    nueva_contraseña = data.get('new_password')
    usuarios[email]['password'] = nueva_contraseña

    return jsonify({'message': 'Contraseña actualizada correctamente'})

