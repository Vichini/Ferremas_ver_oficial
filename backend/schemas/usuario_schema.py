from marshmallow import Schema, fields

class UsuarioRegistroSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True, load_only=True)
    rol = fields.String(required=False)  # 👈 nuevo campo
