from flask import Blueprint, request, jsonify
from extensions import db
from models.usuario import Usuario
from schemas.usuario_schema import UsuarioRegistroSchema
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)
registro_schema = UsuarioRegistroSchema()

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    errors = registro_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    if Usuario.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Usuario ya existe"}), 409

    nuevo_usuario = Usuario(
        username=data['username'],
        rol=data.get('rol', 'usuario')  # 👈 se asigna 'usuario' por defecto
    )
    nuevo_usuario.set_password(data['password'])
    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({"message": "Usuario creado exitosamente"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = Usuario.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        token = create_access_token(identity=user.id)
        return jsonify({
            "access_token": token,
            "rol": user.rol  # 👈 útil para mostrar en frontend
        })
    return jsonify({"message": "Credenciales inválidas"}), 401
