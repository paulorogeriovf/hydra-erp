# Hydra ERP
# Responsável por: concentrar as regras de negócio relacionadas
# aos piscineiros, seus resultados financeiros, clientes,
# produtos vendidos e histórico de movimentações.

from decimal import Decimal
from datetime import date

from sqlalchemy import func

from app.extensions import db

from app.models.piscineiro import Piscineiro
from app.models.notinha import Notinha
from app.models.item_notinha import ItemNotinha

from app.services.notinha_service import NotinhaService
from app.services.comissao_service import ComissaoService
from app.services.movimentacao_service import MovimentacaoService


class PiscineiroService:

    # =========================================================
    # LISTAR
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


    # =========================================================
    # LISTAR ATIVOS
    # =========================================================

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
    # BUSCAR
    # =========================================================

    @staticmethod
    def buscar_por_id(piscineiro_id):

        return db.session.get(
            Piscineiro,
            piscineiro_id
        )


    # =========================================================
    # CRIAR
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

            nome=
                nome,

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


            # =================================================
            # AUDITORIA
            # =================================================

            MovimentacaoService.registrar(

                tipo=
                    "PISCINEIRO",

                acao=
                    "CRIAR",

                descricao=(
                    f"Piscineiro "
                    f"{piscineiro.nome} cadastrado."
                ),

                entidade=
                    "PISCINEIRO",

                entidade_id=
                    piscineiro.id
            )


            return piscineiro


        except Exception:

            db.session.rollback()

            raise


    # =========================================================
    # EDITAR
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


        # =====================================================
        # VALORES ANTERIORES
        # =====================================================

        nome_anterior = (
            piscineiro.nome
        )

        telefone_anterior = (
            piscineiro.telefone
        )

        whatsapp_anterior = (
            piscineiro.whatsapp
        )

        cidade_anterior = (
            piscineiro.cidade
        )

        endereco_anterior = (
            piscineiro.endereco
        )

        observacao_anterior = (
            piscineiro.observacao
        )


        # =====================================================
        # ALTERAR
        # =====================================================

        piscineiro.nome = (
            nome
        )

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


        # =====================================================
        # IDENTIFICAR ALTERAÇÕES
        # =====================================================

        alteracoes = []


        if (
            nome_anterior
            != piscineiro.nome
        ):

            alteracoes.append(
                f"nome: {nome_anterior} "
                f"→ {piscineiro.nome}"
            )


        if (
            telefone_anterior
            != piscineiro.telefone
        ):

            alteracoes.append(
                "telefone alterado"
            )


        if (
            whatsapp_anterior
            != piscineiro.whatsapp
        ):

            alteracoes.append(
                "WhatsApp alterado"
            )


        if (
            cidade_anterior
            != piscineiro.cidade
        ):

            alteracoes.append(
                "cidade alterada"
            )


        if (
            endereco_anterior
            != piscineiro.endereco
        ):

            alteracoes.append(
                "endereço alterado"
            )


        if (
            observacao_anterior
            != piscineiro.observacao
        ):

            alteracoes.append(
                "observação alterada"
            )


        try:

            db.session.commit()


            if alteracoes:

                MovimentacaoService.registrar(

                    tipo=
                        "PISCINEIRO",

                    acao=
                        "EDITAR",

                    descricao=(
                        f"Piscineiro "
                        f"{piscineiro.nome} atualizado. "
                        f"Alterações: "
                        f"{'; '.join(alteracoes)}."
                    ),

                    entidade=
                        "PISCINEIRO",

                    entidade_id=
                        piscineiro.id
                )


            return piscineiro


        except Exception:

            db.session.rollback()

            raise


    # =========================================================
    # ALTERAR STATUS
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


            status_texto = (
                "ativado"
                if piscineiro.ativo
                else "inativado"
            )


            MovimentacaoService.registrar(

                tipo=
                    "PISCINEIRO",

                acao=
                    "STATUS",

                descricao=(
                    f"Piscineiro "
                    f"{piscineiro.nome} "
                    f"{status_texto}."
                ),

                entidade=
                    "PISCINEIRO",

                entidade_id=
                    piscineiro.id
            )


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


        total_vendido = Decimal(
            "0.00"
        )

        total_vendido_mes = Decimal(
            "0.00"
        )

        total_vendido_3_meses = Decimal(
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


        hoje = date.today()


        for notinha in notinhas:

            quantidade_notinhas += 1


            valor = Decimal(
                str(
                    notinha.valor_total
                )
            )


            total_vendido += (
                valor
            )


            # =================================================
            # TOTAL DO MÊS ATUAL
            # =================================================

            if (
                notinha.data_retirada.year
                == hoje.year
                and
                notinha.data_retirada.month
                == hoje.month
            ):

                total_vendido_mes += (
                    valor
                )


            # =================================================
            # ÚLTIMOS 3 MESES
            # =================================================

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


            if (
                0 <= diferenca_meses <= 2
            ):

                total_vendido_3_meses += (
                    valor
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


            total_pendente += (
                saldo
            )


            if (
                "VENCIDA"
                in situacao
            ):

                quantidade_vencidas += 1

                total_vencido += (
                    saldo
                )


            dados_notinhas.append({

                "notinha":
                    notinha,

                "saldo":
                    saldo,

                "situacao":
                    situacao
            })


        comissao_disponivel = (
            ComissaoService.saldo_disponivel(
                piscineiro.id
            )
        )


        return {

            "total_vendido":
                total_vendido,

            "total_vendido_mes":
                total_vendido_mes,

            "total_vendido_3_meses":
                total_vendido_3_meses,

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
    def produtos_mais_vendidos(piscineiro_id):

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
                Notinha.piscineiro_id
                == piscineiro_id,

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
                10
            )
            .all()
        )


    # =========================================================
    # VENDAS DOS ÚLTIMOS MESES
    # =========================================================

    @staticmethod
    def vendas_ultimos_meses(
        piscineiro_id,
        quantidade_meses=6
    ):

        hoje = date.today()

        meses = []


        for deslocamento in range(
            quantidade_meses - 1,
            -1,
            -1
        ):

            mes = (
                hoje.month
                - deslocamento
            )

            ano = (
                hoje.year
            )


            while mes <= 0:

                mes += 12
                ano -= 1


            meses.append(
                (
                    ano,
                    mes
                )
            )


        labels = []

        valores = []


        nomes_meses = [
            "",
            "Jan",
            "Fev",
            "Mar",
            "Abr",
            "Mai",
            "Jun",
            "Jul",
            "Ago",
            "Set",
            "Out",
            "Nov",
            "Dez"
        ]


        for ano, mes in meses:

            total = (
                db.session.query(
                    func.coalesce(
                        func.sum(
                            Notinha.valor_total
                        ),
                        0
                    )
                )
                .filter(
                    Notinha.piscineiro_id
                    == piscineiro_id,

                    Notinha.status
                    != "CANCELADA",

                    func.year(
                        Notinha.data_retirada
                    )
                    == ano,

                    func.month(
                        Notinha.data_retirada
                    )
                    == mes
                )
                .scalar()
            )


            labels.append(
                f"{nomes_meses[mes]}/{str(ano)[2:]}"
            )


            valores.append(
                float(
                    total or 0
                )
            )


        return {

            "labels":
                labels,

            "valores":
                valores
        }