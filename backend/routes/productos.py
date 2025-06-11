from flask import Blueprint, request, jsonify,send_file
from models.producto import Producto
from schemas.producto_schema import ProductoSchema
from extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from io import BytesIO
import openpyxl


productos_bp = Blueprint('productos', __name__)


producto_schema = ProductoSchema()
productos_schema = ProductoSchema(many=True)

@productos_bp.route("/", methods=["GET"])
def listar_productos():
    # Obtener parámetros de query string
    nombre = request.args.get("nombre")
    marca = request.args.get("marca")
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    # Comenzar consulta base
    query = Producto.query

    # Aplicar filtros si existen
    if nombre:
        query = query.filter(Producto.nombre.ilike(f"%{nombre}%"))
    if marca:
        query = query.filter(Producto.marca.ilike(f"%{marca}%"))

    # Paginación
    paginacion = query.paginate(page=page, per_page=per_page, error_out=False)
    productos = paginacion.items

    # Respuesta paginada
    return jsonify({
        "total": paginacion.total,
        "page": paginacion.page,
        "per_page": paginacion.per_page,
        "productos": productos_schema.dump(productos)
    })


@productos_bp.route("/", methods=["POST"])
@jwt_required()
def crear_producto():
    data = request.get_json()
    try:
        nuevo_producto = producto_schema.load(data)
        db.session.add(nuevo_producto)
        db.session.commit()
        return producto_schema.jsonify(nuevo_producto), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@productos_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
def actualizar_producto(id):
    producto = Producto.query.get_or_404(id)
    data = request.get_json()
    try:
        producto_actualizado = producto_schema.load(data, instance=producto)
        db.session.commit()
        return producto_schema.jsonify(producto_actualizado)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@productos_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    return jsonify({"mensaje": "Producto eliminado correctamente"})

@productos_bp.route("/exportar", methods=["GET"])
@jwt_required()
def exportar_productos():
    productos = Producto.query.all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Productos"


    encabezados = ["ID", "Código", "Nombre", "Marca", "Precio", "Stock"]
    ws.append(encabezados)

    
    for p in productos:
        ws.append([p.id, p.codigo, p.nombre, p.marca, p.precio, p.stock])


    archivo = BytesIO()
    wb.save(archivo)
    archivo.seek(0)

    return send_file(
        archivo,
        download_name="productos.xlsx",
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
