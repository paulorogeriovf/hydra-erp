# Hydra ERP
# Responsável por: representar o histórico de ações
# importantes realizadas dentro do sistema.

from datetime import datetime

from app.extensions import db


class Movimentacao(db.Model):

    __tablename__ = "movimentacoes"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    tipo = db.Column(
        db.String(50),
        nullable=False
    )


    acao = db.Column(
        db.String(50),
        nullable=False
    )


    descricao = db.Column(
        db.Text,
        nullable=False
    )


    entidade = db.Column(
        db.String(50),
        nullable=True
    )


    entidade_id = db.Column(
        db.Integer,
        nullable=True
    )


    # Futuramente será ligado ao usuário logado.
    usuario_id = db.Column(
        db.Integer,
        nullable=True
    )


    data_criacao = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now
    )


    def __repr__(self):

        return (
            f"<Movimentacao "
            f"{self.tipo} "
            f"{self.acao}>"
        )