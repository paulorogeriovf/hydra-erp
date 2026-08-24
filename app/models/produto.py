# Hydra ERP
# Responsável por: representar os produtos cadastrados no sistema.

from datetime import datetime

from app.extensions import db


class Produto(db.Model):
    __tablename__ = "produtos"

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(
        db.String(150),
        nullable=False
    )

    marca = db.Column(
        db.String(100),
        nullable=True
    )

    categoria = db.Column(
        db.String(100),
        nullable=True
    )

    preco_normal = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    preco_atacado = db.Column(
        db.Numeric(10, 2),
        nullable=True
    )

    gera_comissao = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    percentual_comissao = db.Column(
        db.Numeric(5, 2),
        nullable=True
    )

    ativo = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    observacao = db.Column(
        db.Text,
        nullable=True
    )

    data_criacao = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    data_atualizacao = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )