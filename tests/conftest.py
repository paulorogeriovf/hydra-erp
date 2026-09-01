import os
import sys
from datetime import date, timedelta
from decimal import Decimal

import pytest
from dotenv import load_dotenv


# =========================================================
# CAMINHO DO PROJETO
# =========================================================

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

if BASE_DIR not in sys.path:
    sys.path.insert(
        0,
        BASE_DIR
    )


from app import create_app
from app.extensions import db
from app.models.cliente import Cliente
from app.models.produto import Produto
from app.services.notinha_service import NotinhaService


load_dotenv(
    os.path.join(
        BASE_DIR,
        ".env"
    )
)


# =========================================================
# APP DE TESTES
# =========================================================

@pytest.fixture
def app():

    test_database_url = os.getenv(
        "TEST_DATABASE_URL"
    )

    if not test_database_url:
        raise RuntimeError(
            "TEST_DATABASE_URL não configurada no .env"
        )

    # Proteção para nunca utilizar o banco normal
    if "hydra_erp_test" not in test_database_url:
        raise RuntimeError(
            "SEGURANÇA: os testes devem utilizar "
            "exclusivamente o banco hydra_erp_test."
        )

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": test_database_url
    })

    with app.app_context():

        db.drop_all()
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


# =========================================================
# CLIENTE HTTP
# =========================================================

@pytest.fixture
def client(app):

    return app.test_client()


# =========================================================
# FACTORY DE NOTINHA
# =========================================================

@pytest.fixture
def criar_notinha(app):

    def _criar(
        valor="500.00",
        vencimento=None
    ):

        cliente = Cliente(
            nome="Cliente Teste Pytest",
            ativo=True
        )

        db.session.add(
            cliente
        )


        produto = Produto(
            nome="Produto Teste Pytest",
            marca="Teste",
            categoria="Teste",
            preco_normal=Decimal(valor),
            gera_comissao=False,
            ativo=True
        )

        db.session.add(
            produto
        )

        db.session.commit()


        if vencimento is None:

            vencimento = (
                date.today()
                + timedelta(days=30)
            )


        notinha = NotinhaService.criar_notinha(
            cliente_id=cliente.id,
            data_retirada=(
                date.today()
                - timedelta(days=30)
                if vencimento < date.today()
                else date.today()
            ),
            data_vencimento=vencimento,
            itens=[
                {
                    "produto_id": produto.id,
                    "quantidade": 1,
                    "preco_unitario": valor
                }
            ],
            responsavel_cobranca="HYDRA"
        )

        return notinha


    return _criar