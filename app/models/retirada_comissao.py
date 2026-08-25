# Hydra ERP
# Responsável por: registrar retiradas parciais ou totais
# das comissões acumuladas pelos piscineiros.

from datetime import datetime

from app.extensions import db


class RetiradaComissao(db.Model):
    __tablename__ = "retiradas_comissao"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    piscineiro_id = db.Column(
        db.Integer,
        db.ForeignKey("piscineiros.id"),
        nullable=False
    )

    valor = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    observacao = db.Column(
        db.Text,
        nullable=True
    )

    data_retirada = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    piscineiro = db.relationship(
        "Piscineiro"
    )