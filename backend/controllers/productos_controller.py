from extensions import db
from models.producto import Producto

def obtener_todos_los_productos():
    return Producto.query.all()

def crear_producto(data):
    nuevo_producto = Producto(**data)
    db.session.add(nuevo_producto)
    db.session.commit()
    return nuevo_producto
