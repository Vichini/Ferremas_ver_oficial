# backend/schemas/producto_schema.py
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models.producto import Producto

class ProductoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Producto
        load_instance = True

    id = auto_field(dump_only=True)
    codigo = auto_field(required=True)
    nombre = auto_field(required=True)
    marca = auto_field()
    precio = auto_field()
    stock = auto_field()
