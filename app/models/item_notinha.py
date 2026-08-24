# Hydra ERP
# Responsável por: representar os produtos e valores registrados em cada notinha.

from app.extensions import db


class ItemNotinha(db.Model):
    __tablename__ = "itens_notinha"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    notinha_id = db.Column(
        db.Integer,
        db.ForeignKey("notinhas.id"),
        nullable=False
    )

    produto_id = db.Column(
        db.Integer,
        db.ForeignKey("produtos.id"),
        nullable=False
    )

    quantidade = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    preco_unitario = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    subtotal = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    # Snapshot para preservar o histórico caso o cadastro mude.
    nome_produto = db.Column(
        db.String(150),
        nullable=False
    )

    marca_produto = db.Column(
        db.String(100),
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

    valor_comissao = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=0
    )

    notinha = db.relationship(
        "Notinha",
        back_populates="itens"
    )

    produto = db.relationship(
        "Produto"
    )