# Hydra ERP
# Responsável por: representar as notinhas e suas informações principais.

from datetime import datetime

from app.extensions import db


class Notinha(db.Model):
    __tablename__ = "notinhas"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey("clientes.id"),
        nullable=False
    )

    # Snapshot do piscineiro responsável no momento da venda.
    # Pode ser NULL para venda direta da Hydra.
    piscineiro_id = db.Column(
        db.Integer,
        db.ForeignKey("piscineiros.id"),
        nullable=True
    )

    data_retirada = db.Column(
        db.Date,
        nullable=False
    )

    data_vencimento = db.Column(
        db.Date,
        nullable=False
    )

    valor_total = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=0
    )

    # ABERTA, PARCIAL, PAGA ou CANCELADA
    status = db.Column(
        db.String(20),
        nullable=False,
        default="ABERTA"
    )

    # HYDRA ou PISCINEIRO
    responsavel_cobranca = db.Column(
        db.String(20),
        nullable=False,
        default="PISCINEIRO"
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

    cliente = db.relationship(
        "Cliente"
    )

    piscineiro = db.relationship(
        "Piscineiro"
    )

    itens = db.relationship(
        "ItemNotinha",
        back_populates="notinha",
        cascade="all, delete-orphan"
    )

    pagamentos = db.relationship(
        "Pagamento",
        back_populates="notinha",
        cascade="all, delete-orphan"
    )

    anexos = db.relationship(
        "AnexoNotinha",
        back_populates="notinha",
        cascade="all, delete-orphan"
    )

    observacoes = db.relationship(
        "ObservacaoNotinha",
        back_populates="notinha",
        cascade="all, delete-orphan"
    )