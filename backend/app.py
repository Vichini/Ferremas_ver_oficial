from flask import Flask
from config import Config
from extensions import db
from models import producto  # <-- esto importa tu modelo
from routes.productos import productos_bp  # <-- esto importa tu blueprint

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(productos_bp, url_prefix="/api/productos")

    with app.app_context():
        db.create_all()

    # Solo para depurar rutas activas
    for rule in app.url_map.iter_rules():
        print(rule)

    return app

app = create_app()

@app.route("/ping")
def ping():
    return "pong"

if __name__ == "__main__":
    app.run(debug=True)
