from sqlalchemy import text

from app.extensions import db


def test_banco_de_testes(app):

    banco_atual = db.session.execute(
        text("SELECT DATABASE()")
    ).scalar()

    assert banco_atual == "hydra_erp_test"