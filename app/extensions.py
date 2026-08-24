# Hydra ERP
# Responsável por: inicializar as extensões utilizadas pela aplicação.

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()