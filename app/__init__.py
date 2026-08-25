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

    # Importa os models para que o SQLAlchemy e o Flask-Migrate
    # reconheçam as tabelas da aplicação.
    from app import models

    # Importa os Blueprints da aplicação.
    from app.routes.dashboard import dashboard_bp
    from app.routes.produtos import produtos_bp
    from app.routes.piscineiros import piscineiros_bp
    from app.routes.clientes import clientes_bp
    from app.routes.orcamentos import orcamentos_bp
    from app.routes.notinhas import notinhas_bp

    # Registra as rotas no Flask.
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(produtos_bp)
    app.register_blueprint(piscineiros_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(orcamentos_bp)
    app.register_blueprint(notinhas_bp)

    return app