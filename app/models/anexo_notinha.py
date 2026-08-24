# Hydra ERP
# Responsável por: registrar fotos, comprovantes e outros arquivos ligados às notinhas.

from datetime import datetime

from app.extensions import db


class AnexoNotinha(db.Model):
    __tablename__ = "anexos_notinha"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    notinha_id = db.Column(
        db.Integer,
        db.ForeignKey("notinhas.id"),
        nullable=False
    )

    # Opcionalmente relaciona o anexo a um pagamento específico.
    pagamento_id = db.Column(
        db.Integer,
        db.ForeignKey("pagamentos.id"),
        nullable=True
    )

    # ORIGINAL, ATUALIZACAO, COMPROVANTE ou OUTRO
    tipo = db.Column(
        db.String(30),
        nullable=False,
        default="OUTRO"
    )

    nome_original = db.Column(
        db.String(255),
        nullable=False
    )

    nome_arquivo = db.Column(
        db.String(255),
        nullable=False
    )

    caminho = db.Column(
        db.String(500),
        nullable=False
    )

    observacao = db.Column(
        db.Text,
        nullable=True
    )

    data_upload = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    notinha = db.relationship(
        "Notinha",
        back_populates="anexos"
    )

    pagamento = db.relationship(
        "Pagamento"
    )