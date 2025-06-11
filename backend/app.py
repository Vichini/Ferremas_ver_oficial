# backend/app.py
from flask import Flask
from dotenv import load_dotenv
from config import Config
from extensions import db, jwt
from routes.productos import productos_bp
from routes.auth import auth_bp  

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)


    db.init_app(app)
    jwt.init_app(app)


    app.register_blueprint(productos_bp, url_prefix="/api/productos")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")  

    
    with app.app_context():
        from models import producto, usuario 
        db.create_all()

    return app

app = create_app()

if __name__ == "__main__":
    app.run()
