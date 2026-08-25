# Hydra ERP
# Responsável por: concentrar as regras de negócio relacionadas aos piscineiros,
# incluindo cadastro, edição, status e resumo financeiro.

from datetime import date, timedelta
from decimal import Decimal
from collections import defaultdict

from app.extensions import db
from app.models.piscineiro import Piscineiro
from app.models.notinha import Notinha
from app.services.notinha_service import NotinhaService
from app.services.comissao_service import ComissaoService
from app.models.item_notinha import ItemNotinha


class PiscineiroService:

    # =========================================================
    # LISTAGEM
    # =========================================================

    @staticmethod
    def listar_piscineiros():

        return (
            Piscineiro.query
            .order_by(
                Piscineiro.nome.asc()
            )
            .all()
        )


    @staticmethod
    def listar_ativos():

        return (
            Piscineiro.query
            .filter_by(
                ativo=True
            )
            .order_by(
                Piscineiro.nome.asc()
            )
            .all()
        )


    # =========================================================
    # BUSCA
    # =========================================================

    @staticmethod
    def buscar_por_id(piscineiro_id):

        return db.session.get(
            Piscineiro,
            piscineiro_id
        )


    # =========================================================
    # CADASTRO
    # =========================================================

    @staticmethod
    def criar_piscineiro(
        nome,
        telefone=None,
        whatsapp=None,
        cidade=None,
        endereco=None,
        observacao=None
    ):

        nome = (
            nome or ""
        ).strip()

        if not nome:

            raise ValueError(
                "O nome do piscineiro é obrigatório."
            )

        piscineiro = Piscineiro(
            nome=nome,

            telefone=(
                telefone or ""
            ).strip() or None,

            whatsapp=(
                whatsapp or ""
            ).strip() or None,

            cidade=(
                cidade or ""
            ).strip() or None,

            endereco=(
                endereco or ""
            ).strip() or None,

            observacao=(
                observacao or ""
            ).strip() or None
        )

        try:

            db.session.add(
                piscineiro
            )

            db.session.commit()

            return piscineiro

        except Exception:

            db.session.rollback()

            raise


    # =========================================================
    # EDIÇÃO
    # =========================================================

    @staticmethod
    def editar_piscineiro(
        piscineiro_id,
        nome,
        telefone=None,
        whatsapp=None,
        cidade=None,
        endereco=None,
        observacao=None
    ):

        piscineiro = (
            PiscineiroService.buscar_por_id(
                piscineiro_id
            )
        )

        if not piscineiro:

            raise ValueError(
                "Piscineiro não encontrado."
            )

        nome = (
            nome or ""
        ).strip()

        if not nome:

            raise ValueError(
                "O nome do piscineiro é obrigatório."
            )

        piscineiro.nome = nome

        piscineiro.telefone = (
            telefone or ""
        ).strip() or None

        piscineiro.whatsapp = (
            whatsapp or ""
        ).strip() or None

        piscineiro.cidade = (
            cidade or ""
        ).strip() or None

        piscineiro.endereco = (
            endereco or ""
        ).strip() or None

        piscineiro.observacao = (
            observacao or ""
        ).strip() or None

        try:

            db.session.commit()

            return piscineiro

        except Exception:

            db.session.rollback()

            raise


    # =========================================================
    # ATIVAR / INATIVAR
    # =========================================================

    @staticmethod
    def alternar_status(piscineiro_id):

        piscineiro = (
            PiscineiroService.buscar_por_id(
                piscineiro_id
            )
        )

        if not piscineiro:

            raise ValueError(
                "Piscineiro não encontrado."
            )

        piscineiro.ativo = (
            not piscineiro.ativo
        )

        try:

            db.session.commit()

            return piscineiro

        except Exception:

            db.session.rollback()

            raise


    # =========================================================
    # RESUMO FINANCEIRO
    # =========================================================

    @staticmethod
    def resumo_financeiro(piscineiro_id):

        piscineiro = (
            PiscineiroService.buscar_por_id(
                piscineiro_id
            )
        )

        if not piscineiro:

            raise ValueError(
                "Piscineiro não encontrado."
            )


        # =====================================================
        # PERÍODOS
        # =====================================================

        hoje = date.today()

        inicio_30_dias = (
            hoje - timedelta(days=30)
        )

        inicio_90_dias = (
            hoje - timedelta(days=90)
        )


        # =====================================================
        # NOTINHAS DO PISCINEIRO
        # =====================================================

        notinhas = (
            Notinha.query
            .filter(
                Notinha.piscineiro_id
                == piscineiro.id,

                Notinha.status
                != "CANCELADA"
            )
            .order_by(
                Notinha.data_retirada.desc()
            )
            .all()
        )


        # =====================================================
        # TOTAIS
        # =====================================================

        total_vendido = Decimal(
            "0.00"
        )

        total_30_dias = Decimal(
            "0.00"
        )

        total_90_dias = Decimal(
            "0.00"
        )

        total_pendente = Decimal(
            "0.00"
        )

        total_vencido = Decimal(
            "0.00"
        )

        quantidade_notinhas = 0

        quantidade_vencidas = 0

        dados_notinhas = []


        # =====================================================
        # PROCESSAR NOTINHAS
        # =====================================================

        for notinha in notinhas:

            quantidade_notinhas += 1

            valor_notinha = Decimal(
                str(
                    notinha.valor_total
                )
            )


            # Total histórico
            total_vendido += (
                valor_notinha
            )


            # Últimos 30 dias
            if (
                notinha.data_retirada
                >= inicio_30_dias
            ):

                total_30_dias += (
                    valor_notinha
                )


            # Últimos 90 dias
            if (
                notinha.data_retirada
                >= inicio_90_dias
            ):

                total_90_dias += (
                    valor_notinha
                )


            # Saldo atual
            saldo = (
                NotinhaService.saldo_pendente(
                    notinha
                )
            )


            # Situação atual
            situacao = (
                NotinhaService.situacao(
                    notinha
                )
            )


            total_pendente += (
                saldo
            )


            # Vencidas
            if "VENCIDA" in situacao:

                quantidade_vencidas += 1

                total_vencido += (
                    saldo
                )


            # Dados usados no histórico
            dados_notinhas.append({
                "notinha": notinha,
                "saldo": saldo,
                "situacao": situacao
            })


        # =====================================================
        # COMISSÃO DISPONÍVEL
        # =====================================================

        comissao_disponivel = (
            ComissaoService.saldo_disponivel(
                piscineiro.id
            )
        )


        # =====================================================
        # RETORNO
        # =====================================================

        return {
            "total_vendido":
                total_vendido,

            "total_30_dias":
                total_30_dias,

            "total_90_dias":
                total_90_dias,

            "total_pendente":
                total_pendente,

            "total_vencido":
                total_vencido,

            "quantidade_notinhas":
                quantidade_notinhas,

            "quantidade_vencidas":
                quantidade_vencidas,

            "comissao_disponivel":
                comissao_disponivel,

            "notinhas":
                dados_notinhas
        }

        # =========================================================
    # PRODUTOS MAIS VENDIDOS
    # =========================================================

    @staticmethod
    def produtos_mais_vendidos(
        piscineiro_id,
        limite=10
    ):

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
                Notinha.piscineiro_id
                == piscineiro_id,

                Notinha.status
                != "CANCELADA"
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
    # VENDAS DOS ÚLTIMOS 6 MESES
    # =========================================================

    @staticmethod
    def vendas_ultimos_meses(
        piscineiro_id,
        quantidade_meses=6
    ):

        hoje = date.today()

        meses = []

        ano = hoje.year
        mes = hoje.month


        # Cria a sequência dos últimos meses.
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


        # Coloca em ordem cronológica.
        meses.reverse()


        totais = defaultdict(
            lambda: Decimal("0.00")
        )


        notinhas = (
            Notinha.query
            .filter(
                Notinha.piscineiro_id
                == piscineiro_id,

                Notinha.status
                != "CANCELADA"
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