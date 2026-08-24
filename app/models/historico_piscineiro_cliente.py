# Hydra ERP
# Responsável por: registrar as mudanças de piscineiro responsável por cada cliente.

from datetime import datetime

from app.extensions import db


class HistoricoPiscineiroCliente(db.Model):
    __tablename__ = "historico_piscineiro_cliente"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey("clientes.id"),
        nullable=False
    )

    piscineiro_anterior_id = db.Column(
        db.Integer,
        db.ForeignKey("piscineiros.id"),
        nullable=True
    )

    piscineiro_novo_id = db.Column(
        db.Integer,
        db.ForeignKey("piscineiros.id"),
        nullable=True
    )

    data_alteracao = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    observacao = db.Column(
        db.Text,
        nullable=True
    )

    cliente = db.relationship(
        "Cliente",
        foreign_keys=[cliente_id]
    )

    piscineiro_anterior = db.relationship(
        "Piscineiro",
        foreign_keys=[piscineiro_anterior_id]
    )

    piscineiro_novo = db.relationship(
        "Piscineiro",
        foreign_keys=[piscineiro_novo_id]
    )