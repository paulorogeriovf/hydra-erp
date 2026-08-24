# Hydra ERP
# Responsável por: criar e configurar a aplicação Flask.

from flask import Flask

from config import Config
from app.extensions import db, migrate


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models

    from app.routes.produtos import produtos_bp
    app.register_blueprint(produtos_bp)

    @app.route("/")
    def home():
        return "Hydra ERP funcionando!"

    return app