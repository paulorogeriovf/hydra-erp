# Hydra ERP
# Responsável por: analisar vendas, clientes, produtos
# e padrões de compra para gerar inteligência comercial.

from datetime import date
from decimal import Decimal

from sqlalchemy import func

from app.extensions import db

from app.models.notinha import Notinha
from app.models.item_notinha import ItemNotinha
from app.models.cliente import Cliente
from app.models.piscineiro import Piscineiro


class InteligenciaVendasService:

    # =========================================================
    # VISÃO GERAL
    # =========================================================

    @staticmethod
    def resumo_geral():

        hoje = date.today()

        notinhas = (
            Notinha.query
            .filter(
                Notinha.status != "CANCELADA"
            )
            .all()
        )

        total_mes = Decimal("0.00")
        total_3_meses = Decimal("0.00")

        quantidade_mes = 0

        clientes_mes = set()


        for notinha in notinhas:

            valor = Decimal(
                str(notinha.valor_total)
            )

            diferenca_meses = (
                (
                    hoje.year
                    - notinha.data_retirada.year
                )
                * 12
                +
                (
                    hoje.month
                    - notinha.data_retirada.month
                )
            )


            # MÊS ATUAL

            if diferenca_meses == 0:

                total_mes += valor

                quantidade_mes += 1

                clientes_mes.add(
                    notinha.cliente_id
                )


            # ÚLTIMOS 3 MESES

            if 0 <= diferenca_meses <= 2:

                total_3_meses += valor


        ticket_medio = Decimal("0.00")


        if quantidade_mes > 0:

            ticket_medio = (
                total_mes
                / quantidade_mes
            )


        return {

            "total_mes":
                total_mes,

            "total_3_meses":
                total_3_meses,

            "quantidade_vendas_mes":
                quantidade_mes,

            "clientes_mes":
                len(clientes_mes),

            "ticket_medio":
                ticket_medio
        }


    # =========================================================
    # RANKING DE PRODUTOS
    # =========================================================

    @staticmethod
    def ranking_produtos(
        limite=10
    ):

        return (
            db.session.query(

                ItemNotinha.nome_produto,

                func.sum(
                    ItemNotinha.quantidade
                ).label(
                    "quantidade_total"
                ),

                func.sum(
                    ItemNotinha.subtotal
                ).label(
                    "valor_total"
                )
            )
            .join(
                Notinha,
                ItemNotinha.notinha_id
                == Notinha.id
            )
            .filter(
                Notinha.status
                != "CANCELADA"
            )
            .group_by(
                ItemNotinha.nome_produto
            )
            .order_by(
                func.sum(
                    ItemNotinha.quantidade
                ).desc()
            )
            .limit(
                limite
            )
            .all()
        )


    # =========================================================
    # RANKING DE CLIENTES
    # =========================================================

    @staticmethod
    def ranking_clientes(
        limite=10
    ):

        return (
            db.session.query(

                Cliente,

                func.sum(
                    Notinha.valor_total
                ).label(
                    "valor_total"
                ),

                func.count(
                    Notinha.id
                ).label(
                    "quantidade_notinhas"
                ),

                func.max(
                    Notinha.data_retirada
                ).label(
                    "ultima_compra"
                )
            )
            .join(
                Notinha,
                Notinha.cliente_id
                == Cliente.id
            )
            .filter(
                Notinha.status
                != "CANCELADA"
            )
            .group_by(
                Cliente.id
            )
            .order_by(
                func.sum(
                    Notinha.valor_total
                ).desc()
            )
            .limit(
                limite
            )
            .all()
        )


    # =========================================================
    # RANKING DE PISCINEIROS
    # =========================================================

    @staticmethod
    def ranking_piscineiros(
        limite=10
    ):

        return (
            db.session.query(

                Piscineiro,

                func.sum(
                    Notinha.valor_total
                ).label(
                    "valor_total"
                ),

                func.count(
                    Notinha.id
                ).label(
                    "quantidade_notinhas"
                )
            )
            .join(
                Notinha,
                Notinha.piscineiro_id
                == Piscineiro.id
            )
            .filter(
                Notinha.status
                != "CANCELADA"
            )
            .group_by(
                Piscineiro.id
            )
            .order_by(
                func.sum(
                    Notinha.valor_total
                ).desc()
            )
            .limit(
                limite
            )
            .all()
        )


    # =========================================================
    # CLIENTES SEM COMPRAR
    # =========================================================

    @staticmethod
    def clientes_sem_comprar(
        dias_minimos=30
    ):

        hoje = date.today()

        clientes = (
            Cliente.query
            .filter_by(
                ativo=True
            )
            .order_by(
                Cliente.nome.asc()
            )
            .all()
        )


        resultado = []


        for cliente in clientes:

            ultima_compra = (
                db.session.query(
                    func.max(
                        Notinha.data_retirada
                    )
                )
                .filter(
                    Notinha.cliente_id
                    == cliente.id,

                    Notinha.status
                    != "CANCELADA"
                )
                .scalar()
            )


            # Cliente cadastrado,
            # mas nunca comprou.
            if not ultima_compra:

                resultado.append({

                    "cliente":
                        cliente,

                    "ultima_compra":
                        None,

                    "dias_sem_comprar":
                        None,

                    "nunca_comprou":
                        True
                })

                continue


            dias_sem_comprar = (
                hoje
                - ultima_compra
            ).days


            if (
                dias_sem_comprar
                >= dias_minimos
            ):

                resultado.append({

                    "cliente":
                        cliente,

                    "ultima_compra":
                        ultima_compra,

                    "dias_sem_comprar":
                        dias_sem_comprar,

                    "nunca_comprou":
                        False
                })


        resultado.sort(
            key=lambda item: (
                item["dias_sem_comprar"]
                if item["dias_sem_comprar"]
                is not None
                else 999999
            ),
            reverse=True
        )


        return resultado