# Hydra ERP
# Responsável por: registrar pagamentos totais ou parciais das notinhas.

from datetime import datetime

from app.extensions import db


class Pagamento(db.Model):
    __tablename__ = "pagamentos"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    notinha_id = db.Column(
        db.Integer,
        db.ForeignKey("notinhas.id"),
        nullable=False
    )

    valor = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    data_pagamento = db.Column(
        db.Date,
        nullable=False
    )

    # CLIENTE, PISCINEIRO ou OUTRO
    pago_por = db.Column(
        db.String(20),
        nullable=False,
        default="CLIENTE"
    )

    forma_pagamento = db.Column(
        db.String(30),
        nullable=True
    )

    observacao = db.Column(
        db.Text,
        nullable=True
    )

    data_registro = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    notinha = db.relationship(
        "Notinha",
        back_populates="pagamentos"
    )