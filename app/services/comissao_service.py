# Hydra ERP
# Responsável por: calcular comissões acumuladas,
# retiradas, saldo disponível e origem das comissões
# dos piscineiros.

from decimal import Decimal, InvalidOperation

from sqlalchemy import func

from app.extensions import db
from app.models.piscineiro import Piscineiro
from app.models.notinha import Notinha
from app.models.item_notinha import ItemNotinha
from app.models.retirada_comissao import RetiradaComissao
from app.services.movimentacao_service import MovimentacaoService


class ComissaoService:

    # =========================================================
    # CONVERSÃO DE VALORES
    # =========================================================

    @staticmethod
    def _converter_decimal(valor, campo):

        try:

            numero = Decimal(
                str(valor).replace(",", ".")
            )

            if numero <= 0:
                raise ValueError(
                    f"{campo} deve ser maior que zero."
                )

            return numero

        except (
            InvalidOperation,
            TypeError,
            ValueError
        ):

            raise ValueError(
                f"{campo} possui um valor inválido."
            )


    # =========================================================
    # TOTAL DE COMISSÃO GERADA
    # =========================================================

    @staticmethod
    def total_gerado(piscineiro_id):

        total = (
            db.session.query(
                func.coalesce(
                    func.sum(
                        ItemNotinha.valor_comissao
                    ),
                    0
                )
            )
            .join(
                Notinha,
                ItemNotinha.notinha_id == Notinha.id
            )
            .filter(
                Notinha.piscineiro_id == piscineiro_id,
                ItemNotinha.valor_comissao > 0,
                Notinha.status != "CANCELADA"
            )
            .scalar()
        )

        return Decimal(
            str(total)
        )


    # =========================================================
    # TOTAL JÁ RETIRADO
    # =========================================================

    @staticmethod
    def total_retirado(piscineiro_id):

        total = (
            db.session.query(
                func.coalesce(
                    func.sum(
                        RetiradaComissao.valor
                    ),
                    0
                )
            )
            .filter(
                RetiradaComissao.piscineiro_id
                == piscineiro_id
            )
            .scalar()
        )

        return Decimal(
            str(total)
        )


    # =========================================================
    # SALDO DISPONÍVEL
    # =========================================================

    @staticmethod
    def saldo_disponivel(piscineiro_id):

        saldo = (
            ComissaoService.total_gerado(
                piscineiro_id
            )
            -
            ComissaoService.total_retirado(
                piscineiro_id
            )
        )

        if saldo < 0:
            return Decimal("0.00")

        return saldo


    # =========================================================
    # LISTAGEM GERAL DOS PISCINEIROS
    # =========================================================

    @staticmethod
    def listar_piscineiros():

        piscineiros = (
            Piscineiro.query
            .order_by(
                Piscineiro.nome.asc()
            )
            .all()
        )

        resultado = []

        for piscineiro in piscineiros:

            gerado = (
                ComissaoService.total_gerado(
                    piscineiro.id
                )
            )

            retirado = (
                ComissaoService.total_retirado(
                    piscineiro.id
                )
            )

            saldo = (
                gerado
                -
                retirado
            )

            if saldo < 0:
                saldo = Decimal("0.00")

            resultado.append({
                "piscineiro": piscineiro,
                "gerado": gerado,
                "retirado": retirado,
                "saldo": saldo
            })

        return resultado


    # =========================================================
    # REGISTRAR RETIRADA
    # =========================================================

    @staticmethod
    def registrar_retirada(
        piscineiro_id,
        valor,
        observacao=None
    ):

        piscineiro = db.session.get(
            Piscineiro,
            int(piscineiro_id)
        )

        if not piscineiro:

            raise ValueError(
                "Piscineiro não encontrado."
            )

        valor = (
            ComissaoService._converter_decimal(
                valor,
                "Valor da retirada"
            )
        )

        saldo = (
            ComissaoService.saldo_disponivel(
                piscineiro.id
            )
        )

        if valor > saldo:

            raise ValueError(
                f"A retirada não pode ser maior "
                f"que o saldo disponível de "
                f"R$ {saldo:.2f}."
            )

        retirada = RetiradaComissao(
            piscineiro_id=piscineiro.id,
            valor=valor,
            observacao=(
                observacao or ""
            ).strip() or None
        )

        try:

            db.session.add(
                retirada
            )

            db.session.commit()

            MovimentacaoService.registrar(
    tipo="COMISSAO",
    acao="RETIRADA",
    descricao=(
        f"Retirada de comissão de "
        f"R$ {retirada.valor:.2f} registrada para "
        f"{piscineiro.nome}."
    ),
    entidade="PISCINEIRO",
    entidade_id=piscineiro.id
)

            return retirada

        except Exception:

            db.session.rollback()

            raise


    # =========================================================
    # HISTÓRICO DE RETIRADAS
    # =========================================================

    @staticmethod
    def listar_retiradas(piscineiro_id):

        return (
            RetiradaComissao.query
            .filter_by(
                piscineiro_id=piscineiro_id
            )
            .order_by(
                RetiradaComissao.data_retirada.desc()
            )
            .all()
        )


    # =========================================================
    # ORIGEM DAS COMISSÕES
    # =========================================================

    @staticmethod
    def listar_origens(piscineiro_id):

        resultados = (
            db.session.query(
                ItemNotinha,
                Notinha
            )
            .join(
                Notinha,
                ItemNotinha.notinha_id == Notinha.id
            )
            .filter(
                Notinha.piscineiro_id == piscineiro_id,
                ItemNotinha.valor_comissao > 0,
                Notinha.status != "CANCELADA"
            )
            .order_by(
                Notinha.data_retirada.desc(),
                ItemNotinha.id.desc()
            )
            .all()
        )

        origens = []

        for item, notinha in resultados:

            origens.append({
                "notinha": notinha,
                "item": item,
                "cliente": notinha.cliente
            })

        return origens