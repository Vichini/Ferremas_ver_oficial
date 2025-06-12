from flask import Blueprint, request, jsonify, send_file
from models.producto import Producto
from extensions import db
from flask_jwt_extended import jwt_required
from io import BytesIO
import openpyxl

productos_bp = Blueprint('productos', __name__)

@productos_bp.route("/", methods=["GET"])
def listar_productos():
    nombre = request.args.get("nombre")
    marca = request.args.get("marca")
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    query = Producto.query
    if nombre:
        query = query.filter(Producto.nombre.ilike(f"%{nombre}%"))
    if marca:
        query = query.filter(Producto.marca.ilike(f"%{marca}%"))

    paginacion = query.paginate(page=page, per_page=per_page, error_out=False)
    productos = paginacion.items

    return jsonify({
        "total": paginacion.total,
        "page": paginacion.page,
        "per_page": paginacion.per_page,
        "productos": [
            {
                "id": p.id,
                "codigo": p.codigo,
                "nombre": p.nombre,
                "marca": p.marca,
                "precio": p.precio,
                "stock": p.stock
            }
            for p in productos
        ]
    })

@productos_bp.route("/", methods=["POST"])
@productos_bp.route("", methods=["POST"])
@jwt_required()
def crear_producto():
    data = request.get_json()
    try:
        print("💾 Recibido:", data)
        nuevo_producto = Producto(
            codigo=data.get("codigo"),
            nombre=data.get("nombre"),
            marca=data.get("marca"),
            precio=float(data.get("precio")),
            stock=int(data.get("stock"))
        )
        db.session.add(nuevo_producto)
        db.session.commit()
        return jsonify({"mensaje": "Producto creado exitosamente"}), 201
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@productos_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
def actualizar_producto(id):
    producto = Producto.query.get_or_404(id)
    data = request.get_json()
    try:
        producto.codigo = data.get("codigo")
        producto.nombre = data.get("nombre")
        producto.marca = data.get("marca")
        producto.precio = float(data.get("precio"))
        producto.stock = int(data.get("stock"))
        db.session.commit()
        return jsonify({"mensaje": "Producto actualizado exitosamente"})
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
