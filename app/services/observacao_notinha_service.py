# Hydra ERP
# Responsável por: registrar e consultar o histórico
# de observações e acontecimentos das notinhas.

from app.extensions import db
from app.models.notinha import Notinha
from app.models.observacao_notinha import ObservacaoNotinha


class ObservacaoNotinhaService:

    @staticmethod
    def listar_por_notinha(notinha_id):

        return (
            ObservacaoNotinha.query
            .filter_by(notinha_id=notinha_id)
            .order_by(ObservacaoNotinha.data_criacao.desc())
            .all()
        )

    @staticmethod
    def adicionar(
        notinha_id,
        texto
    ):

        notinha = db.session.get(
            Notinha,
            int(notinha_id)
        )

        if not notinha:
            raise ValueError(
                "Notinha não encontrada."
            )

        texto = (
            texto or ""
        ).strip()

        if not texto:
            raise ValueError(
                "A observação não pode ficar vazia."
            )

        observacao = ObservacaoNotinha(
            notinha_id=notinha.id,
            texto=texto
        )

        try:

            db.session.add(
                observacao
            )

            db.session.commit()

            return observacao

        except Exception:

            db.session.rollback()

            raise