# backend/decorators.py
from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify
from models.usuario import Usuario

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        usuario = Usuario.query.get(user_id)
        if usuario is None or usuario.rol != "admin":
            return jsonify({"error": "Acceso restringido a administradores"}), 403
        return fn(*args, **kwargs)
    return wrapper
