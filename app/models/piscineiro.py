# Hydra ERP
# Responsável por: representar os piscineiros cadastrados no sistema.

from datetime import datetime

from app.extensions import db


class Piscineiro(db.Model):
    __tablename__ = "piscineiros"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(150),
        nullable=False
    )

    telefone = db.Column(
        db.String(20),
        nullable=True
    )

    whatsapp = db.Column(
        db.String(20),
        nullable=True
    )

    cidade = db.Column(
        db.String(100),
        nullable=True
    )

    endereco = db.Column(
        db.String(255),
        nullable=True
    )

    observacao = db.Column(
        db.Text,
        nullable=True
    )

    ativo = db.Column(
        db.Boolean,
        nullable=False,
        default=True
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

    clientes = db.relationship(
        "Cliente",
        back_populates="piscineiro",
        lazy=True
    )