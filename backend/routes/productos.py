from flask import Blueprint, jsonify, request
from controllers.productos_controller import obtener_todos_los_productos, crear_producto
from schemas.producto_schema import ProductoSchema

productos_bp = Blueprint("productos", __name__)
producto_schema = ProductoSchema()
productos_schema = ProductoSchema(many=True)

@productos_bp.route("/", methods=["GET"])
def get_productos():
    productos = obtener_todos_los_productos()
    return productos_schema.dump(productos), 200

@productos_bp.route("/", methods=["POST"])
def post_producto():
    json_data = request.get_json()
    if not json_data:
        return {"error": "No se enviaron datos"}, 400

    errors = producto_schema.validate(json_data)
    if errors:
        return {"errores": errors}, 422

    producto = crear_producto(json_data)
    return producto_schema.dump(producto), 201
