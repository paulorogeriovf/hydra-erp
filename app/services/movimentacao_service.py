# Hydra ERP
# Responsável por: registrar e consultar
# o histórico de movimentações do sistema.

from app.extensions import db
from app.models.movimentacao import Movimentacao


class MovimentacaoService:

    # =========================================================
    # REGISTRAR
    # =========================================================

    @staticmethod
    def registrar(
        tipo,
        acao,
        descricao,
        entidade=None,
        entidade_id=None,
        usuario_id=None
    ):

        tipo = (
            tipo or ""
        ).strip().upper()

        acao = (
            acao or ""
        ).strip().upper()

        descricao = (
            descricao or ""
        ).strip()


        if not tipo:
            raise ValueError(
                "O tipo da movimentação é obrigatório."
            )


        if not acao:
            raise ValueError(
                "A ação da movimentação é obrigatória."
            )


        if not descricao:
            raise ValueError(
                "A descrição da movimentação é obrigatória."
            )


        movimentacao = Movimentacao(

            tipo=
                tipo,

            acao=
                acao,

            descricao=
                descricao,

            entidade=(
                entidade or ""
            ).strip().upper() or None,

            entidade_id=
                entidade_id,

            usuario_id=
                usuario_id
        )


        db.session.add(
            movimentacao
        )

        db.session.commit()


        return movimentacao


    # =========================================================
    # LISTAR
    # =========================================================

    @staticmethod
    def listar(
        limite=200
    ):

        return (
            Movimentacao.query
            .order_by(
                Movimentacao.data_criacao.desc()
            )
            .limit(
                limite
            )
            .all()
        )


    # =========================================================
    # FILTRAR POR TIPO
    # =========================================================

    @staticmethod
    def listar_por_tipo(
        tipo,
        limite=200
    ):

        tipo = (
            tipo or ""
        ).strip().upper()


        return (
            Movimentacao.query
            .filter_by(
                tipo=tipo
            )
            .order_by(
                Movimentacao.data_criacao.desc()
            )
            .limit(
                limite
            )
            .all()
        )