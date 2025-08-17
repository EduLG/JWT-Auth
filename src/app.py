import os
from flask import Flask, request, jsonify, url_for, send_from_directory # Se añade send_from_directory
from flask_migrate import Migrate
from flask_cors import CORS
from api.utils import APIException, generate_sitemap
from api.admin import setup_admin
from api.models import db, User
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, JWTManager
from flask_jwt_extended import jwt_required, get_jwt_identity


# Instancia de la aplicación y la configuración
ENV = os.getenv("FLASK_ENV", "development") # Valor por defecto
static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../public/')
app = Flask(__name__)
app.url_map.strict_slashes = False

# Configuración de la base de datos
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db, compare_type = True)
db.init_app(app)

# Habilita CORS
CORS(app)

# Configuración del administrador
setup_admin(app)

# Inicializa Flask-Bcrypt
bcrypt = Bcrypt(app)

# Configuración de JWT
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-key") # Valor por defecto
jwt = JWTManager(app)


# Manejo de errores
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    if ENV == "development":
        return generate_sitemap(app)
    return send_from_directory(static_file_dir, 'index.html')

# ----------------- RUTA DE REGISTRO -----------------
@app.route('/signup', methods=['POST'])
def handle_signup():
    body = request.get_json()
    email = body.get('email')
    password = body.get('password')

    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400

    user_exists = User.query.filter_by(email=email).first()
    if user_exists:
        return jsonify({"msg": "Email already exists"}), 409

    try:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(email=email, password=hashed_password, is_active=True)
        db.session.add(new_user)
        db.session.commit()
        response_body = {
            "msg": "Usuario registrado exitosamente"
        }
        return jsonify(response_body), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error al registrar usuario: {e}"}), 500

# ----------------- RUTA DE INICIO DE SESIÓN -----------------

@app.route("/token", methods=["POST"])
def create_token():
    body = request.get_json() # Se cambia a request.get_json()
    email = body.get("email", None)
    password = body.get("password", None)

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"msg": "Bad username or password"}), 401
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({
        "token": access_token,
        "user": user.serialize()
    })

# ----------------- INICIO: RUTA PRIVADA -----------------

@app.route("/private", methods=["GET"])
@jwt_required()
def get_private_data():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user:
        return jsonify({
            "msg": f"¡Hola {user.email}! Esto es un mensaje privado. Solo lo ves porque estás autenticado.",
            "user": user.serialize()
        }), 200
    return jsonify({"msg": "User not found"}), 404

# ----------------- FIN: RUTAS DE AUTENTICACIÓN -----------------

@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    user_list = [user.serialize() for user in users]
    return jsonify(user_list), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)