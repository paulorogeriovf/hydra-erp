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

from collections import defaultdict
from statistics import mean


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

        # =========================================================
    # OPORTUNIDADES POR PRODUTO
    # =========================================================

    @staticmethod
    def oportunidades_produtos(
        minimo_compras=3
    ):

        hoje = date.today()

        itens = (
            db.session.query(
                Notinha.cliente_id,
                ItemNotinha.produto_id,
                ItemNotinha.nome_produto,
                Notinha.data_retirada
            )
            .join(
                ItemNotinha,
                ItemNotinha.notinha_id
                == Notinha.id
            )
            .filter(
                Notinha.status
                != "CANCELADA"
            )
            .order_by(
                Notinha.cliente_id.asc(),
                ItemNotinha.produto_id.asc(),
                Notinha.data_retirada.asc()
            )
            .all()
        )


        historico = defaultdict(
            list
        )


        nomes_produtos = {}


        for (
            cliente_id,
            produto_id,
            nome_produto,
            data_retirada
        ) in itens:

            chave = (
                cliente_id,
                produto_id
            )


            historico[
                chave
            ].append(
                data_retirada
            )


            nomes_produtos[
                chave
            ] = (
                nome_produto
            )


        oportunidades = []


        for (
            cliente_id,
            produto_id
        ), datas in historico.items():


            # Precisamos de histórico suficiente.
            if len(datas) < minimo_compras:
                continue


            # =================================================
            # INTERVALOS ENTRE COMPRAS
            # =================================================

            intervalos = []


            for indice in range(
                1,
                len(datas)
            ):

                intervalo = (
                    datas[indice]
                    - datas[indice - 1]
                ).days


                # Ignora duas compras no mesmo dia
                # para não distorcer a frequência.
                if intervalo > 0:

                    intervalos.append(
                        intervalo
                    )


            if not intervalos:
                continue


            media_dias = (
                sum(intervalos)
                / len(intervalos)
            )


            # Evita análises estranhas
            # com frequência muito curta.
            if media_dias < 3:
                continue


            ultima_compra = (
                datas[-1]
            )


            dias_sem_comprar = (
                hoje
                - ultima_compra
            ).days


            proporcao = (
                dias_sem_comprar
                / media_dias
            )


            # =================================================
            # CLASSIFICAÇÃO
            # =================================================

            if proporcao >= 2:

                nivel = (
                    "ALTA"
                )

            elif proporcao >= 1.5:

                nivel = (
                    "ATENCAO"
                )

            else:

                continue


            cliente = db.session.get(
                Cliente,
                cliente_id
            )


            if not cliente:
                continue


            # =================================================
            # CLIENTE CONTINUA COMPRANDO?
            # =================================================

            ultima_compra_geral = (
                db.session.query(
                    func.max(
                        Notinha.data_retirada
                    )
                )
                .filter(
                    Notinha.cliente_id
                    == cliente_id,

                    Notinha.status
                    != "CANCELADA"
                )
                .scalar()
            )


            continua_comprando = (
                ultima_compra_geral
                is not None
                and ultima_compra_geral
                > ultima_compra
            )


            atraso_sobre_media = (
                dias_sem_comprar
                - round(
                    media_dias
                )
            )


            oportunidades.append({

                "cliente":
                    cliente,

                "produto_id":
                    produto_id,

                "produto_nome":
                    nomes_produtos[
                        (
                            cliente_id,
                            produto_id
                        )
                    ],

                "quantidade_compras":
                    len(datas),

                "media_dias":
                    round(
                        media_dias
                    ),

                "ultima_compra":
                    ultima_compra,

                "dias_sem_comprar":
                    dias_sem_comprar,

                "atraso_sobre_media":
                    atraso_sobre_media,

                "proporcao":
                    round(
                        proporcao,
                        2
                    ),

                "nivel":
                    nivel,

                "continua_comprando":
                    continua_comprando,

                "ultima_compra_geral":
                    ultima_compra_geral
            })


        # =====================================================
        # ORDENAR
        # =====================================================

        oportunidades.sort(
            key=lambda item: (
                item["nivel"]
                == "ALTA",

                item["continua_comprando"],

                item["proporcao"]
            ),
            reverse=True
        )


        return oportunidades

        # =========================================================
    # CLIENTES EM RISCO
    # =========================================================

    @staticmethod
    def clientes_em_risco(
        minimo_compras=3
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

            datas = (
                db.session.query(
                    Notinha.data_retirada
                )
                .filter(
                    Notinha.cliente_id
                    == cliente.id,

                    Notinha.status
                    != "CANCELADA"
                )
                .order_by(
                    Notinha.data_retirada.asc()
                )
                .all()
            )


            datas = [
                item[0]
                for item in datas
            ]


            if len(datas) < minimo_compras:
                continue


            intervalos = []


            for indice in range(
                1,
                len(datas)
            ):

                intervalo = (
                    datas[indice]
                    - datas[indice - 1]
                ).days


                if intervalo > 0:

                    intervalos.append(
                        intervalo
                    )


            if not intervalos:
                continue


            media_dias = (
                sum(intervalos)
                / len(intervalos)
            )


            if media_dias < 3:
                continue


            ultima_compra = (
                datas[-1]
            )


            dias_sem_comprar = (
                hoje
                - ultima_compra
            ).days


            proporcao = (
                dias_sem_comprar
                / media_dias
            )


            if proporcao >= 2:

                nivel = "ALTA"

            elif proporcao >= 1.5:

                nivel = "ATENCAO"

            else:

                continue


            resultado.append({

                "cliente":
                    cliente,

                "quantidade_compras":
                    len(datas),

                "media_dias":
                    round(media_dias),

                "ultima_compra":
                    ultima_compra,

                "dias_sem_comprar":
                    dias_sem_comprar,

                "atraso_sobre_media":
                    (
                        dias_sem_comprar
                        - round(media_dias)
                    ),

                "proporcao":
                    round(
                        proporcao,
                        2
                    ),

                "nivel":
                    nivel
            })


        resultado.sort(
            key=lambda item: (
                item["nivel"] == "ALTA",
                item["proporcao"]
            ),
            reverse=True
        )


        return resultado