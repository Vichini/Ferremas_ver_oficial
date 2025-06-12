from flask import Flask, jsonify
from dotenv import load_dotenv
from config import Config
from extensions import db, jwt
from routes.productos import productos_bp
from routes.auth import auth_bp  
from flask_cors import CORS

load_dotenv()

def create_app():
    app = Flask(__name__)

   
    app.url_map.strict_slashes = False
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})

    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(productos_bp, url_prefix="/api/productos")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")  

    
    @app.route("/")
    def index():
        return jsonify({"mensaje": " API Ferremas funcionando. Usa /api/auth o /api/productos"})

    with app.app_context():
        from models import producto, usuario 
        db.create_all()

    return app

app = create_app()

if __name__ == "__main__":
    app.run()
