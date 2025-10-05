import os
from flask import Flask
from flasgger import Swagger
from dotenv import load_dotenv
from app.routes import bp

# Загружаем .env
load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')

    # создаём Swagger UI
    Swagger(app, template_file=None)

    # Регистрируем маршруты
    app.register_blueprint(bp)

    return app

app = create_app()