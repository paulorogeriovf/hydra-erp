# Hydra ERP
# Responsável por: concentrar as regras de negócio relacionadas
# aos clientes, situação financeira, produtos comprados
# e mudanças de piscineiro responsável.

from decimal import Decimal

from app.extensions import db

from app.models.cliente import Cliente
from app.models.piscineiro import Piscineiro
from app.models.notinha import Notinha
from app.models.item_notinha import ItemNotinha
from app.models.historico_piscineiro_cliente import HistoricoPiscineiroCliente

from app.services.notinha_service import NotinhaService
from app.services.movimentacao_service import MovimentacaoService


class ClienteService:

    # =========================================================
    # LISTAR
    # =========================================================

    @staticmethod
    def listar_clientes():

        return (
            Cliente.query
            .order_by(
                Cliente.nome.asc()
            )
            .all()
        )


    # =========================================================
    # BUSCAR
    # =========================================================

    @staticmethod
    def buscar_por_id(cliente_id):

        return db.session.get(
            Cliente,
            cliente_id
        )


    # =========================================================
    # CRIAR CLIENTE
    # =========================================================

    @staticmethod
    def criar_cliente(
        nome,
        telefone=None,
        whatsapp=None,
        endereco=None,
        cidade=None,
        piscineiro_id=None,
        observacao=None
    ):

        nome = (
            nome or ""
        ).strip()


        if not nome:

            raise ValueError(
                "O nome do cliente é obrigatório."
            )


        # =====================================================
        # PISCINEIRO
        # =====================================================

        piscineiro = None


        if piscineiro_id:

            piscineiro = db.session.get(
                Piscineiro,
                int(piscineiro_id)
            )


            if not piscineiro:

                raise ValueError(
                    "Piscineiro selecionado não existe."
                )


            if not piscineiro.ativo:

                raise ValueError(
                    "Não é possível vincular um cliente "
                    "a um piscineiro inativo."
                )


        # =====================================================
        # CLIENTE
        # =====================================================

        cliente = Cliente(

            nome=
                nome,

            telefone=(
                telefone or ""
            ).strip() or None,

            whatsapp=(
                whatsapp or ""
            ).strip() or None,

            endereco=(
                endereco or ""
            ).strip() or None,

            cidade=(
                cidade or ""
            ).strip() or None,

            piscineiro_id=(
                piscineiro.id
                if piscineiro
                else None
            ),

            observacao=(
                observacao or ""
            ).strip() or None
        )


        try:

            db.session.add(
                cliente
            )


            # Precisamos do ID antes
            # de criar o histórico do vínculo.
            db.session.flush()


            # =================================================
            # HISTÓRICO DO VÍNCULO INICIAL
            # =================================================

            if piscineiro:

                historico = (
                    HistoricoPiscineiroCliente(

                        cliente_id=
                            cliente.id,

                        piscineiro_anterior_id=
                            None,

                        piscineiro_novo_id=
                            piscineiro.id,

                        observacao=
                            "Vínculo inicial do cliente."
                    )
                )


                db.session.add(
                    historico
                )


            db.session.commit()


            # =================================================
            # HISTÓRICO GERAL DO ERP
            # =================================================

            descricao = (
                f"Cliente {cliente.nome} cadastrado."
            )


            if piscineiro:

                descricao += (
                    f" Vinculado ao piscineiro "
                    f"{piscineiro.nome}."
                )

            else:

                descricao += (
                    " Cliente sem piscineiro vinculado."
                )


            MovimentacaoService.registrar(

                tipo=
                    "CLIENTE",

                acao=
                    "CRIAR",

                descricao=
                    descricao,

                entidade=
                    "CLIENTE",

                entidade_id=
                    cliente.id
            )


            return cliente


        except Exception:

            db.session.rollback()

            raise


    # =========================================================
    # EDITAR CLIENTE
    # =========================================================

    @staticmethod
    def editar_cliente(
        cliente_id,
        nome,
        telefone=None,
        whatsapp=None,
        endereco=None,
        cidade=None,
        observacao=None
    ):

        cliente = (
            ClienteService.buscar_por_id(
                cliente_id
            )
        )


        if not cliente:

            raise ValueError(
                "Cliente não encontrado."
            )


        nome = (
            nome or ""
        ).strip()


        if not nome:

            raise ValueError(
                "O nome do cliente é obrigatório."
            )


        # =====================================================
        # SNAPSHOT ANTERIOR
        # =====================================================

        nome_anterior = (
            cliente.nome
        )


        telefone_anterior = (
            cliente.telefone
        )


        whatsapp_anterior = (
            cliente.whatsapp
        )


        endereco_anterior = (
            cliente.endereco
        )


        cidade_anterior = (
            cliente.cidade
        )


        observacao_anterior = (
            cliente.observacao
        )


        # =====================================================
        # ALTERAÇÕES
        # =====================================================

        cliente.nome = (
            nome
        )


        cliente.telefone = (
            telefone or ""
        ).strip() or None


        cliente.whatsapp = (
            whatsapp or ""
        ).strip() or None


        cliente.endereco = (
            endereco or ""
        ).strip() or None


        cliente.cidade = (
            cidade or ""
        ).strip() or None


        cliente.observacao = (
            observacao or ""
        ).strip() or None


        # =====================================================
        # DESCOBRIR O QUE MUDOU
        # =====================================================

        alteracoes = []


        if (
            nome_anterior
            != cliente.nome
        ):

            alteracoes.append(
                f"nome: {nome_anterior} → {cliente.nome}"
            )


        if (
            telefone_anterior
            != cliente.telefone
        ):

            alteracoes.append(
                "telefone alterado"
            )


        if (
            whatsapp_anterior
            != cliente.whatsapp
        ):

            alteracoes.append(
                "WhatsApp alterado"
            )


        if (
            endereco_anterior
            != cliente.endereco
        ):

            alteracoes.append(
                "endereço alterado"
            )


        if (
            cidade_anterior
            != cliente.cidade
        ):

            alteracoes.append(
                "cidade alterada"
            )


        if (
            observacao_anterior
            != cliente.observacao
        ):

            alteracoes.append(
                "observação alterada"
            )


        try:

            db.session.commit()


            # Só registra movimentação
            # se realmente houve alguma mudança.
            if alteracoes:

                descricao = (
                    f"Cliente {cliente.nome} atualizado. "
                    f"Alterações: "
                    f"{'; '.join(alteracoes)}."
                )


                MovimentacaoService.registrar(

                    tipo=
                        "CLIENTE",

                    acao=
                        "EDITAR",

                    descricao=
                        descricao,

                    entidade=
                        "CLIENTE",

                    entidade_id=
                        cliente.id
                )


            return cliente


        except Exception:

            db.session.rollback()

            raise


    # =========================================================
    # MUDAR PISCINEIRO
    # =========================================================

    @staticmethod
    def mudar_piscineiro(
        cliente_id,
        novo_piscineiro_id=None,
        observacao=None
    ):

        cliente = (
            ClienteService.buscar_por_id(
                cliente_id
            )
        )


        if not cliente:

            raise ValueError(
                "Cliente não encontrado."
            )


        piscineiro_anterior_id = (
            cliente.piscineiro_id
        )


        piscineiro_anterior = None


        if piscineiro_anterior_id:

            piscineiro_anterior = (
                db.session.get(
                    Piscineiro,
                    piscineiro_anterior_id
                )
            )


        novo_piscineiro = None


        # =====================================================
        # VALIDAR NOVO PISCINEIRO
        # =====================================================

        if novo_piscineiro_id:

            novo_piscineiro = (
                db.session.get(
                    Piscineiro,
                    int(novo_piscineiro_id)
                )
            )


            if not novo_piscineiro:

                raise ValueError(
                    "Piscineiro selecionado não existe."
                )


            if not novo_piscineiro.ativo:

                raise ValueError(
                    "Não é possível vincular o cliente "
                    "a um piscineiro inativo."
                )


        novo_id = (
            novo_piscineiro.id
            if novo_piscineiro
            else None
        )


        if (
            piscineiro_anterior_id
            == novo_id
        ):

            raise ValueError(
                "O cliente já está vinculado "
                "a esse piscineiro."
            )


        # =====================================================
        # ALTERAR VÍNCULO
        # =====================================================

        cliente.piscineiro_id = (
            novo_id
        )


        historico = (
            HistoricoPiscineiroCliente(

                cliente_id=
                    cliente.id,

                piscineiro_anterior_id=
                    piscineiro_anterior_id,

                piscineiro_novo_id=
                    novo_id,

                observacao=(
                    observacao or ""
                ).strip() or None
            )
        )


        try:

            db.session.add(
                historico
            )


            db.session.commit()


            # =================================================
            # NOMES PARA AUDITORIA
            # =================================================

            nome_anterior = (
                piscineiro_anterior.nome
                if piscineiro_anterior
                else "Sem piscineiro"
            )


            nome_novo = (
                novo_piscineiro.nome
                if novo_piscineiro
                else "Sem piscineiro"
            )


            MovimentacaoService.registrar(

                tipo=
                    "CLIENTE",

                acao=
                    "ALTERAR_PISCINEIRO",

                descricao=(
                    f"Piscineiro do cliente "
                    f"{cliente.nome} alterado de "
                    f"{nome_anterior} para "
                    f"{nome_novo}."
                ),

                entidade=
                    "CLIENTE",

                entidade_id=
                    cliente.id
            )


            return cliente


        except Exception:

            db.session.rollback()

            raise


    # =========================================================
    # ALTERNAR STATUS
    # =========================================================

    @staticmethod
    def alternar_status(cliente_id):

        cliente = (
            ClienteService.buscar_por_id(
                cliente_id
            )
        )


        if not cliente:

            raise ValueError(
                "Cliente não encontrado."
            )


        cliente.ativo = (
            not cliente.ativo
        )


        try:

            db.session.commit()


            status_texto = (
                "ativado"
                if cliente.ativo
                else "inativado"
            )


            MovimentacaoService.registrar(

                tipo=
                    "CLIENTE",

                acao=
                    "STATUS",

                descricao=(
                    f"Cliente {cliente.nome} "
                    f"{status_texto}."
                ),

                entidade=
                    "CLIENTE",

                entidade_id=
                    cliente.id
            )


            return cliente


        except Exception:

            db.session.rollback()

            raise


    # =========================================================
    # RESUMO FINANCEIRO
    # =========================================================

    @staticmethod
    def resumo_financeiro(cliente_id):

        cliente = (
            ClienteService.buscar_por_id(
                cliente_id
            )
        )


        if not cliente:

            raise ValueError(
                "Cliente não encontrado."
            )


        notinhas = (
            Notinha.query
            .filter(
                Notinha.cliente_id
                == cliente.id,

                Notinha.status
                != "CANCELADA"
            )
            .order_by(
                Notinha.data_retirada.desc()
            )
            .all()
        )


        total_comprado = Decimal(
            "0.00"
        )

        total_pago = Decimal(
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


        for notinha in notinhas:

            quantidade_notinhas += 1


            valor = Decimal(
                str(
                    notinha.valor_total
                )
            )


            pago = (
                NotinhaService.total_pago(
                    notinha
                )
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


            total_comprado += (
                valor
            )


            total_pago += (
                pago
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

                "pago":
                    pago,

                "saldo":
                    saldo,

                "situacao":
                    situacao
            })


        return {

            "total_comprado":
                total_comprado,

            "total_pago":
                total_pago,

            "total_pendente":
                total_pendente,

            "total_vencido":
                total_vencido,

            "quantidade_notinhas":
                quantidade_notinhas,

            "quantidade_vencidas":
                quantidade_vencidas,

            "notinhas":
                dados_notinhas
        }


    # =========================================================
    # HISTÓRICO DE PISCINEIROS
    # =========================================================

    @staticmethod
    def historico_piscineiros(cliente_id):

        return (
            HistoricoPiscineiroCliente.query
            .filter_by(
                cliente_id=
                    cliente_id
            )
            .order_by(
                HistoricoPiscineiroCliente
                .data_alteracao.desc()
            )
            .all()
        )


    # =========================================================
    # PRODUTOS MAIS COMPRADOS
    # =========================================================

    @staticmethod
    def produtos_mais_comprados(cliente_id):

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
                Notinha.cliente_id
                == cliente_id,

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
                10
            )
            .all()
        )


        return resultados