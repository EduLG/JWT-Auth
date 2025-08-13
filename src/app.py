from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity
from datetime import timedelta

app = Flask(__name__)

# Configuración de la base de datos (SQLite en este caso, por simplicidad)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Configuración de JWT
app.config["JWT_SECRET_KEY"] = "tu-clave-secreta-muy-larga-y-aleatoria"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1) # El token expira en 1 hora
jwt = JWTManager(app)

# Modelo de usuario para la base de datos
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False) # Nota: En un proyecto real, la contraseña debe estar hasheada.
    
    def __repr__(self):
        return f'<User {self.email}>'

# Puntos de conexión (endpoints)

# Endpoint para registrar un nuevo usuario
@app.route("/signup", methods=["POST"])
def signup():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    if not email or not password:
        return jsonify({"msg": "Email y contraseña son requeridos"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "El email ya existe"}), 409

    # Aquí se crea un usuario simple, en la vida real, hashearías la contraseña
    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "Usuario creado exitosamente"}), 201

# Endpoint para iniciar sesión y obtener el token JWT
@app.route("/token", methods=["POST"])
def create_token():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    user = User.query.filter_by(email=email).first()

    if user is None or user.password != password: # Validación simple
        return jsonify({"msg": "Email o contraseña incorrectos"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200

# Endpoint para una página privada (requiere token JWT)
@app.route("/private", methods=["GET"])
@jwt_required()
def private():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    return jsonify(
        id=user.id,
        email=user.email,
        message="¡Hola! Esta es una página privada."
    ), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Esto crea la tabla de usuarios si no existe
    app.run(debug=True)