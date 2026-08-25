# Hydra ERP
# Responsável por: concentrar as regras de negócio relacionadas
# à criação, consulta, situação financeira e cobrança das notinhas.

from datetime import date
from decimal import Decimal, InvalidOperation

from sqlalchemy import func

from app.extensions import db
from app.models.notinha import Notinha
from app.models.item_notinha import ItemNotinha
from app.models.cliente import Cliente
from app.models.produto import Produto
from app.models.pagamento import Pagamento


class NotinhaService:

    # =====================================================
    # BUSCA
    # =====================================================

    @staticmethod
    def buscar_por_id(notinha_id):

        return db.session.get(
            Notinha,
            notinha_id
        )


    # =====================================================
    # LISTAGEM
    # =====================================================

    @staticmethod
    def listar_notinhas():

        return (
            Notinha.query
            .order_by(
                Notinha.data_criacao.desc()
            )
            .all()
        )


    # =====================================================
    # CONVERSÃO DECIMAL
    # =====================================================

    @staticmethod
    def _converter_decimal(valor, campo):

        try:

            numero = Decimal(
                str(valor).replace(",", ".")
            )

            if numero < 0:

                raise ValueError(
                    f"{campo} não pode ser negativo."
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


    # =====================================================
    # CRIAR NOTINHA
    # =====================================================

    @staticmethod
    def criar_notinha(
        cliente_id,
        data_retirada,
        data_vencimento,
        itens,
        responsavel_cobranca="PISCINEIRO",
        observacao=None
    ):

        # =========================
        # CLIENTE
        # =========================

        if not cliente_id:

            raise ValueError(
                "O cliente é obrigatório."
            )


        cliente = db.session.get(
            Cliente,
            int(cliente_id)
        )


        if not cliente:

            raise ValueError(
                "Cliente não encontrado."
            )


        if not cliente.ativo:

            raise ValueError(
                "Não é possível criar uma notinha "
                "para um cliente inativo."
            )


        # =========================
        # DATAS
        # =========================

        if not data_retirada:

            raise ValueError(
                "A data da retirada é obrigatória."
            )


        if not data_vencimento:

            raise ValueError(
                "A data de vencimento é obrigatória."
            )


        if data_vencimento < data_retirada:

            raise ValueError(
                "A data de vencimento não pode "
                "ser anterior à data da retirada."
            )


        # =========================
        # ITENS
        # =========================

        if not itens:

            raise ValueError(
                "A notinha precisa possuir "
                "pelo menos um produto."
            )


        # =========================
        # RESPONSÁVEL COBRANÇA
        # =========================

        responsavel_cobranca = (
            responsavel_cobranca
            or "PISCINEIRO"
        ).upper()


        if responsavel_cobranca not in {
            "HYDRA",
            "PISCINEIRO"
        }:

            raise ValueError(
                "Responsável pela cobrança inválido."
            )


        # Cliente sem piscineiro:
        # cobrança automaticamente fica com a Hydra.
        if (
            cliente.piscineiro_id is None
            and responsavel_cobranca == "PISCINEIRO"
        ):

            responsavel_cobranca = "HYDRA"


        # =========================
        # CRIAR NOTINHA
        # =========================

        notinha = Notinha(

            cliente_id=
                cliente.id,

            # Snapshot do piscineiro no momento da venda.
            piscineiro_id=
                cliente.piscineiro_id,

            data_retirada=
                data_retirada,

            data_vencimento=
                data_vencimento,

            valor_total=
                Decimal("0.00"),

            status=
                "ABERTA",

            responsavel_cobranca=
                responsavel_cobranca,

            observacao=(
                observacao or ""
            ).strip() or None
        )


        try:

            db.session.add(
                notinha
            )


            # Gera o ID sem confirmar a transação.
            db.session.flush()


            valor_total = Decimal(
                "0.00"
            )


            # =========================
            # PROCESSAR PRODUTOS
            # =========================

            for item in itens:

                produto_id = (
                    item.get(
                        "produto_id"
                    )
                )


                if not produto_id:

                    raise ValueError(
                        "Produto inválido na notinha."
                    )


                # QUANTIDADE

                quantidade = (
                    NotinhaService
                    ._converter_decimal(
                        item.get(
                            "quantidade"
                        ),
                        "Quantidade"
                    )
                )


                if quantidade <= 0:

                    raise ValueError(
                        "A quantidade deve ser "
                        "maior que zero."
                    )


                # PRODUTO

                produto = db.session.get(
                    Produto,
                    int(produto_id)
                )


                if not produto:

                    raise ValueError(
                        "Um dos produtos selecionados "
                        "não existe."
                    )


                if not produto.ativo:

                    raise ValueError(
                        f"O produto '{produto.nome}' "
                        f"está inativo."
                    )


                # =========================
                # PREÇO
                # =========================

                preco_informado = (
                    item.get(
                        "preco_unitario"
                    )
                )


                if (
                    preco_informado is None
                    or str(
                        preco_informado
                    ).strip() == ""
                ):

                    preco_unitario = Decimal(
                        str(
                            produto.preco_normal
                        )
                    )

                else:

                    preco_unitario = (
                        NotinhaService
                        ._converter_decimal(
                            preco_informado,
                            "Preço unitário"
                        )
                    )


                if preco_unitario <= 0:

                    raise ValueError(
                        "O preço unitário deve ser "
                        "maior que zero."
                    )


                subtotal = (
                    quantidade
                    * preco_unitario
                )


                # =========================
                # COMISSÃO
                # =========================

                gera_comissao = bool(
                    produto.gera_comissao
                )


                percentual_comissao = None


                valor_comissao = Decimal(
                    "0.00"
                )


                if (
                    gera_comissao
                    and produto.percentual_comissao
                    is not None
                    and cliente.piscineiro_id
                    is not None
                ):

                    percentual_comissao = Decimal(
                        str(
                            produto.percentual_comissao
                        )
                    )


                    valor_comissao = (
                        subtotal
                        * percentual_comissao
                        / Decimal("100")
                    )


                # =========================
                # ITEM DA NOTINHA
                # =========================

                item_notinha = ItemNotinha(

                    notinha_id=
                        notinha.id,

                    produto_id=
                        produto.id,

                    quantidade=
                        quantidade,

                    preco_unitario=
                        preco_unitario,

                    subtotal=
                        subtotal,

                    # Snapshot do produto.
                    nome_produto=
                        produto.nome,

                    marca_produto=
                        produto.marca,

                    # Snapshot da comissão.
                    gera_comissao=
                        gera_comissao,

                    percentual_comissao=
                        percentual_comissao,

                    valor_comissao=
                        valor_comissao
                )


                db.session.add(
                    item_notinha
                )


                valor_total += (
                    subtotal
                )


            # =========================
            # TOTAL FINAL
            # =========================

            if valor_total <= 0:

                raise ValueError(
                    "O valor total da notinha "
                    "deve ser maior que zero."
                )


            notinha.valor_total = (
                valor_total
            )


            db.session.commit()


            return notinha


        except Exception:

            db.session.rollback()

            raise


    # =====================================================
    # TOTAL JÁ PAGO
    # =====================================================

    @staticmethod
    def total_pago(notinha):

        total = (
            db.session.query(
                func.coalesce(
                    func.sum(
                        Pagamento.valor
                    ),
                    0
                )
            )
            .filter(
                Pagamento.notinha_id
                == notinha.id
            )
            .scalar()
        )


        return Decimal(
            str(total)
        )


    # =====================================================
    # SALDO PENDENTE
    # =====================================================

    @staticmethod
    def saldo_pendente(notinha):

        valor_total = Decimal(
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
            valor_total
            - pago
        )


        if saldo < 0:

            return Decimal(
                "0.00"
            )


        return saldo


    # =====================================================
    # VERIFICAR VENCIMENTO
    # =====================================================

    @staticmethod
    def esta_vencida(notinha):

        if notinha.status in {
            "PAGA",
            "CANCELADA"
        }:

            return False


        saldo = (
            NotinhaService.saldo_pendente(
                notinha
            )
        )


        return (
            saldo > 0
            and notinha.data_vencimento
            < date.today()
        )


    # =====================================================
    # SITUAÇÃO PARA EXIBIÇÃO
    # =====================================================

    @staticmethod
    def situacao(notinha):

        if notinha.status == "CANCELADA":

            return "CANCELADA"


        if notinha.status == "PAGA":

            return "PAGA"


        if (
            NotinhaService.esta_vencida(
                notinha
            )
        ):

            if (
                notinha.status
                == "PARCIAL"
            ):

                return (
                    "PARCIAL_VENCIDA"
                )


            return "VENCIDA"


        if notinha.status == "PARCIAL":

            return "PARCIAL"


        return "ABERTA"


    # =====================================================
    # DIAS DE ATRASO
    # =====================================================

    @staticmethod
    def dias_atraso(notinha):

        if not notinha.data_vencimento:

            return 0


        if notinha.status in {
            "PAGA",
            "CANCELADA"
        }:

            return 0


        hoje = date.today()


        if (
            notinha.data_vencimento
            >= hoje
        ):

            return 0


        diferenca = (
            hoje
            - notinha.data_vencimento
        )


        return diferenca.days


    # =====================================================
    # MENSAGEM INDIVIDUAL DE COBRANÇA
    # =====================================================

    @staticmethod
    def mensagem_cobranca(notinha):

        if not notinha:

            raise ValueError(
                "Notinha não encontrada."
            )


        saldo = (
            NotinhaService.saldo_pendente(
                notinha
            )
        )


        # Sem saldo, não existe cobrança.
        if saldo <= 0:

            return None


        dias = (
            NotinhaService.dias_atraso(
                notinha
            )
        )


        # Cobranças só serão usadas
        # para notinhas vencidas.
        if dias <= 0:

            return None


        # =========================
        # NOMES
        # =========================

        cliente_nome = (
            notinha.cliente.nome
            if notinha.cliente
            else "Cliente"
        )


        piscineiro_nome = (
            notinha.piscineiro.nome
            if notinha.piscineiro
            else None
        )


        # =========================
        # DATAS
        # =========================

        data_retirada = (
            notinha.data_retirada
            .strftime(
                "%d/%m/%Y"
            )
        )


        data_vencimento = (
            notinha.data_vencimento
            .strftime(
                "%d/%m/%Y"
            )
        )


        # =========================
        # VALOR
        # =========================

        valor_formatado = (
            f"{saldo:,.2f}"
            .replace(
                ",",
                "X"
            )
            .replace(
                ".",
                ","
            )
            .replace(
                "X",
                "."
            )
        )


        # =========================
        # ATRASO
        # =========================

        texto_atraso = (

            "1 dia de atraso"

            if dias == 1

            else (
                f"{dias} dias de atraso"
            )
        )


        # =================================================
        # HYDRA COBRA O CLIENTE
        # =================================================

        if (
            notinha.responsavel_cobranca
            == "HYDRA"
        ):

            if piscineiro_nome:

                origem = (
                    f"a notinha retirada pelo "
                    f"*{piscineiro_nome}*"
                )

            else:

                origem = (
                    "a notinha retirada "
                    "diretamente na Hydra"
                )


            return (

                f"Olá, *{cliente_nome}*! "
                f"Tudo bem? 😊\n\n"

                f"Verificamos que {origem}, "
                f"no dia *{data_retirada}*, "
                f"com saldo pendente de "
                f"*R$ {valor_formatado}*, "
                f"ainda consta em aberto "
                f"conosco.\n\n"

                f"O vencimento foi em "
                f"*{data_vencimento}* e "
                f"atualmente está com "
                f"*{texto_atraso}*.\n\n"

                f"Poderia confirmar para nós "
                f"se esse pagamento já foi "
                f"realizado? Obrigado! 😊"
            )


        # =================================================
        # PISCINEIRO É RESPONSÁVEL
        # =================================================

        if (
            notinha.responsavel_cobranca
            == "PISCINEIRO"
        ):

            if not piscineiro_nome:

                return None


            return (

                f"Olá, *{piscineiro_nome}*! "
                f"Tudo bem? 😊\n\n"

                f"Verificamos que a notinha "
                f"do seu cliente "
                f"*{cliente_nome}*, retirada "
                f"no dia *{data_retirada}*, "
                f"com saldo pendente de "
                f"*R$ {valor_formatado}*, "
                f"ainda consta em aberto "
                f"conosco.\n\n"

                f"O vencimento foi em "
                f"*{data_vencimento}* e "
                f"atualmente está com "
                f"*{texto_atraso}*.\n\n"

                f"Poderia verificar para nós "
                f"se esse pagamento já foi "
                f"realizado? Obrigado! 😊"
            )


        return None