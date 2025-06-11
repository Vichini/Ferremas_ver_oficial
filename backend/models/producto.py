from extensions import db  

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(100), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(100))
    precio = db.Column(db.Float)
    stock = db.Column(db.Integer)
