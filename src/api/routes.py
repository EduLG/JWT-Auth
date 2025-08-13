"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import request, jsonify, Blueprint
from api.models import db, User
from api.utils import generate_sitemap, APIException
from flask_cors import CORS

from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_bcrypt import Bcrypt

api = Blueprint('api', __name__)
# Allow CORS requests to this API
CORS(api)
bcrypt = Bcrypt()


@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():
    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }
    return jsonify(response_body), 200


@api.route('/login', methods=['POST'])
def login_user():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'A request body is required'}), 400
    if 'email' not in body:
        return jsonify({'msg': 'The email field is required'}), 400
    if 'password' not in body:
        return jsonify({'msg': 'The password field is required'}), 400

    user_found = User.query.filter_by(email=body['email']).first()
    if user_found is None:
        return jsonify({'msg': 'Incorrect email or password'}), 400

    password_valid = bcrypt.check_password_hash(
        user_found.password, body['password'])
    if not password_valid:
        return jsonify({'msg': 'Incorrect email or password'}), 400

    access_token = create_access_token(identity=user_found.email)
    print(user_found)
    return jsonify({'msg': 'ok', 'token': access_token, 'user': user_found.email}), 200


@api.route('/signup', methods=['POST'])
def create_user():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'A request body is required'}), 400
    if 'email' not in body:
        return jsonify({'msg': 'The email field is required'}), 400
    if 'password' not in body:
        return jsonify({'msg': 'The password field is required'}), 400

    user_exists = User.query.filter_by(email=body['email']).first()
    if user_exists:
        return jsonify({'msg': 'User already exists'}), 409

    new_user = User(
        email=body['email'],
        password=bcrypt.generate_password_hash(body['password']).decode('utf-8'),
        is_active=True
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'msg': f'User {new_user} successfully registered'}), 200


@api.route('/protected', methods=['GET'])
@jwt_required()
def protected_view():
    current_user = get_jwt_identity()
    return jsonify({'msg': f'Accessing private information for {current_user}'}), 200