# Hydra ERP
# Responsável por: consolidar os principais indicadores,
# rankings e gráficos utilizados no Dashboard do sistema.

from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from app.extensions import db

from app.models.notinha import Notinha
from app.models.item_notinha import ItemNotinha
from app.models.piscineiro import Piscineiro

from app.services.notinha_service import NotinhaService
from app.services.comissao_service import ComissaoService


class DashboardService:

    # =========================================================
    # RESUMO FINANCEIRO
    # =========================================================

    @staticmethod
    def resumo():

        notinhas = (
            Notinha.query
            .filter(
                Notinha.status != "CANCELADA"
            )
            .all()
        )

        total_receber = Decimal("0.00")
        total_vencido = Decimal("0.00")

        quantidade_pendentes = 0
        quantidade_vencidas = 0

        vendas_30_dias = Decimal("0.00")

        hoje = date.today()

        inicio_30_dias = (
            hoje - timedelta(days=30)
        )

        for notinha in notinhas:

            valor_notinha = Decimal(
                str(notinha.valor_total)
            )

            # Vendas recentes
            if (
                notinha.data_retirada
                >= inicio_30_dias
            ):
                vendas_30_dias += (
                    valor_notinha
                )

            saldo = (
                NotinhaService.saldo_pendente(
                    notinha
                )
            )

            situacao = (
                NotinhaService.situacao(
                    notinha
                )
            )

            if saldo > 0:

                quantidade_pendentes += 1

                total_receber += saldo

            if "VENCIDA" in situacao:

                quantidade_vencidas += 1

                total_vencido += saldo


        # Comissão disponível de todos os piscineiros
        comissoes_disponiveis = Decimal(
            "0.00"
        )

        piscineiros = (
            Piscineiro.query
            .all()
        )

        for piscineiro in piscineiros:

            comissoes_disponiveis += (
                ComissaoService.saldo_disponivel(
                    piscineiro.id
                )
            )


        return {
            "total_receber":
                total_receber,

            "total_vencido":
                total_vencido,

            "quantidade_pendentes":
                quantidade_pendentes,

            "quantidade_vencidas":
                quantidade_vencidas,

            "vendas_30_dias":
                vendas_30_dias,

            "comissoes_disponiveis":
                comissoes_disponiveis
        }


    # =========================================================
    # VENDAS DOS ÚLTIMOS 6 MESES
    # =========================================================

    @staticmethod
    def vendas_ultimos_meses(
        quantidade_meses=6
    ):

        hoje = date.today()

        meses = []

        ano = hoje.year
        mes = hoje.month


        for _ in range(
            quantidade_meses
        ):

            meses.append(
                (ano, mes)
            )

            mes -= 1

            if mes == 0:

                mes = 12
                ano -= 1


        meses.reverse()


        totais = defaultdict(
            lambda: Decimal("0.00")
        )


        notinhas = (
            Notinha.query
            .filter(
                Notinha.status != "CANCELADA"
            )
            .all()
        )


        for notinha in notinhas:

            chave = (
                notinha.data_retirada.year,
                notinha.data_retirada.month
            )

            if chave in meses:

                totais[chave] += Decimal(
                    str(notinha.valor_total)
                )


        nomes_meses = {
            1: "Jan",
            2: "Fev",
            3: "Mar",
            4: "Abr",
            5: "Mai",
            6: "Jun",
            7: "Jul",
            8: "Ago",
            9: "Set",
            10: "Out",
            11: "Nov",
            12: "Dez"
        }


        labels = []
        valores = []


        for ano, mes in meses:

            labels.append(
                f"{nomes_meses[mes]}/{str(ano)[2:]}"
            )

            valores.append(
                float(
                    totais[
                        (ano, mes)
                    ]
                )
            )


        return {
            "labels": labels,
            "valores": valores
        }


    # =========================================================
    # TOP PISCINEIROS
    # =========================================================

    @staticmethod
    def top_piscineiros(
        limite=5,
        dias=90
    ):

        inicio = (
            date.today()
            - timedelta(days=dias)
        )


        resultados = (
            db.session.query(
                Piscineiro.id,
                Piscineiro.nome,

                db.func.sum(
                    Notinha.valor_total
                ).label(
                    "valor_total"
                )
            )
            .join(
                Notinha,
                Notinha.piscineiro_id
                == Piscineiro.id
            )
            .filter(
                Notinha.status
                != "CANCELADA",

                Notinha.data_retirada
                >= inicio
            )
            .group_by(
                Piscineiro.id,
                Piscineiro.nome
            )
            .order_by(
                db.func.sum(
                    Notinha.valor_total
                ).desc()
            )
            .limit(
                limite
            )
            .all()
        )


        return resultados


    # =========================================================
    # TOP PRODUTOS
    # =========================================================

    @staticmethod
    def top_produtos(
        limite=5,
        dias=90
    ):

        inicio = (
            date.today()
            - timedelta(days=dias)
        )


        resultados = (
            db.session.query(
                ItemNotinha.nome_produto,

                db.func.sum(
                    ItemNotinha.quantidade
                ).label(
                    "quantidade_total"
                ),

                db.func.sum(
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
                != "CANCELADA",

                Notinha.data_retirada
                >= inicio
            )
            .group_by(
                ItemNotinha.nome_produto
            )
            .order_by(
                db.func.sum(
                    ItemNotinha.quantidade
                ).desc()
            )
            .limit(
                limite
            )
            .all()
        )


        return resultados


    # =========================================================
    # PENDÊNCIAS VENCIDAS
    # =========================================================

    @staticmethod
    def pendencias_vencidas(
        limite=8
    ):

        notinhas = (
            Notinha.query
            .filter(
                Notinha.status.notin_(
                    [
                        "PAGA",
                        "CANCELADA"
                    ]
                )
            )
            .order_by(
                Notinha.data_vencimento.asc()
            )
            .all()
        )


        resultado = []


        for notinha in notinhas:

            situacao = (
                NotinhaService.situacao(
                    notinha
                )
            )

            if "VENCIDA" not in situacao:
                continue


            saldo = (
                NotinhaService.saldo_pendente(
                    notinha
                )
            )


            resultado.append({
                "notinha": notinha,
                "saldo": saldo,
                "situacao": situacao
            })


            if len(resultado) >= limite:
                break


        return resultado