# Hydra ERP
# Responsável por: centralizar as configurações utilizadas pela aplicação.

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data",
        "uploads"
    )

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024