# Hydra ERP
# Responsável por: consolidar os principais indicadores,
# rankings, gráficos, cobranças e inteligência
# utilizados no Dashboard principal.

from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from app.extensions import db

from app.models.notinha import Notinha
from app.models.item_notinha import ItemNotinha
from app.models.piscineiro import Piscineiro

from app.services.notinha_service import NotinhaService
from app.services.comissao_service import ComissaoService
from app.services.cobranca_service import CobrancaService
from app.services.inteligencia_vendas_service import InteligenciaVendasService
from app.services.movimentacao_service import MovimentacaoService


class DashboardService:

    # =========================================================
    # RESUMO PRINCIPAL
    # =========================================================

    @staticmethod
    def resumo():

        # Inteligência de vendas
        vendas = (
            InteligenciaVendasService
            .resumo_geral()
        )

        # Cobranças vencidas e próximas
        cobrancas = (
            CobrancaService.resumo()
        )

        # =====================================================
        # TOTAL A RECEBER
        # =====================================================

        notinhas = (
            Notinha.query
            .filter(
                Notinha.status != "CANCELADA"
            )
            .all()
        )

        total_receber = Decimal("0.00")
        quantidade_pendentes = 0

        for notinha in notinhas:

            saldo = (
                NotinhaService.saldo_pendente(
                    notinha
                )
            )

            if saldo > 0:

                total_receber += saldo

                quantidade_pendentes += 1

        # =====================================================
        # COMISSÕES DISPONÍVEIS
        # =====================================================

        comissoes_disponiveis = Decimal(
            "0.00"
        )

        piscineiros = (
            Piscineiro.query
            .filter_by(
                ativo=True
            )
            .all()
        )

        for piscineiro in piscineiros:

            comissoes_disponiveis += (
                ComissaoService
                .saldo_disponivel(
                    piscineiro.id
                )
            )

        # =====================================================
        # OPORTUNIDADES
        # =====================================================

        oportunidades = (
            InteligenciaVendasService
            .oportunidades_produtos()
        )

        clientes_risco = (
            InteligenciaVendasService
            .clientes_em_risco()
        )

        oportunidades_alta = len([
            item
            for item in oportunidades
            if item["nivel"] == "ALTA"
        ])

        clientes_risco_alta = len([
            item
            for item in clientes_risco
            if item["nivel"] == "ALTA"
        ])

        # =====================================================
        # RETORNO
        # =====================================================

        return {

            # VENDAS
            "vendas_mes":
                vendas["total_mes"],

            "vendas_3_meses":
                vendas["total_3_meses"],

            "ticket_medio":
                vendas["ticket_medio"],

            "clientes_mes":
                vendas["clientes_mes"],

            # COMPATIBILIDADE COM DASHBOARD ANTIGO
            "vendas_30_dias":
                vendas["total_mes"],

            # FINANCEIRO
            "total_receber":
                total_receber,

            "quantidade_pendentes":
                quantidade_pendentes,

            # COBRANÇAS
            "total_vencido":
                cobrancas["total_vencido"],

            "quantidade_vencidas":
                cobrancas["quantidade_vencidas"],

            "quantidade_proximas":
                cobrancas["quantidade_proximas"],

            "total_proximo":
                cobrancas["total_proximo"],

            # COMISSÕES
            "comissoes_disponiveis":
                comissoes_disponiveis,

            # OPORTUNIDADES
            "oportunidades":
                len(oportunidades),

            "oportunidades_alta":
                oportunidades_alta,

            "clientes_risco":
                len(clientes_risco),

            "clientes_risco_alta":
                clientes_risco_alta
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
                    str(
                        notinha.valor_total
                    )
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
    # TOP PISCINEIROS - ÚLTIMOS 90 DIAS
    # =========================================================

    @staticmethod
    def top_piscineiros(
        limite=3,
        dias=90
    ):

        inicio = (
            date.today()
            - timedelta(
                days=dias
            )
        )

        return (
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


    # =========================================================
    # TOP PRODUTOS - ÚLTIMOS 90 DIAS
    # =========================================================

    @staticmethod
    def top_produtos(
        limite=3,
        dias=90
    ):

        inicio = (
            date.today()
            - timedelta(
                days=dias
            )
        )

        return (
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


    # =========================================================
    # PENDÊNCIAS VENCIDAS
    # =========================================================

    @staticmethod
    def pendencias_vencidas(
        limite=8
    ):

        vencidas = (
            CobrancaService
            .listar_vencidas()
        )

        return vencidas[:limite]


    # =========================================================
    # TOP OPORTUNIDADES
    # =========================================================

    @staticmethod
    def top_oportunidades(
        limite=3
    ):

        oportunidades = (
            InteligenciaVendasService
            .oportunidades_produtos()
        )

        return oportunidades[:limite]


    # =========================================================
    # MOVIMENTAÇÕES RECENTES
    # =========================================================

    @staticmethod
    def movimentacoes_recentes(
        limite=3
    ):

        return (
            MovimentacaoService
            .listar(
                limite=limite
            )
        )