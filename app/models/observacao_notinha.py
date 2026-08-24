# Hydra ERP
# Responsável por: manter o histórico de observações e acontecimentos de uma notinha.

from datetime import datetime

from app.extensions import db


class ObservacaoNotinha(db.Model):
    __tablename__ = "observacoes_notinha"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    notinha_id = db.Column(
        db.Integer,
        db.ForeignKey("notinhas.id"),
        nullable=False
    )

    texto = db.Column(
        db.Text,
        nullable=False
    )

    data_criacao = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    notinha = db.relationship(
        "Notinha",
        back_populates="observacoes"
    )