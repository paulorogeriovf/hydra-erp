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
from app.services.movimentacao_service import MovimentacaoService


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

        # CLIENTE

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


        # DATAS

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


        # ITENS

        if not itens:

            raise ValueError(
                "A notinha precisa possuir "
                "pelo menos um produto."
            )


        # RESPONSÁVEL PELA COBRANÇA

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


        if (
            cliente.piscineiro_id is None
            and responsavel_cobranca == "PISCINEIRO"
        ):

            responsavel_cobranca = "HYDRA"


        # CRIAR NOTINHA

        notinha = Notinha(

            cliente_id=
                cliente.id,

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

            db.session.flush()


            valor_total = Decimal(
                "0.00"
            )


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


                quantidade = (
                    NotinhaService._converter_decimal(
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
                        f"O produto '{produto.nome}' está inativo."
                    )


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
                        NotinhaService._converter_decimal(
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


                # COMISSÃO

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

                    nome_produto=
                        produto.nome,

                    marca_produto=
                        produto.marca,

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


            if valor_total <= 0:

                raise ValueError(
                    "O valor total da notinha "
                    "deve ser maior que zero."
                )


            notinha.valor_total = (
                valor_total
            )


            db.session.commit()

            MovimentacaoService.registrar(
    tipo="NOTINHA",
    acao="CRIAR",
    descricao=(
        f"Notinha #{notinha.id} criada para "
        f"{cliente.nome}, no valor de "
        f"R$ {notinha.valor_total:.2f}."
    ),
    entidade="NOTINHA",
    entidade_id=notinha.id
)

            return notinha


        except Exception:

            db.session.rollback()

            raise


    # =====================================================
    # TOTAL PAGO
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
    # SALDO
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
    # SITUAÇÃO
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


        return (
            hoje
            - notinha.data_vencimento
        ).days


    # =====================================================
    # MENSAGEM DE COBRANÇA
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


        if saldo <= 0:
            return None


        dias = (
            NotinhaService.dias_atraso(
                notinha
            )
        )


        if dias <= 0:
            return None


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


        data_retirada = (
            notinha.data_retirada
            .strftime("%d/%m/%Y")
        )


        data_vencimento = (
            notinha.data_vencimento
            .strftime("%d/%m/%Y")
        )


        valor_formatado = (
            f"{saldo:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )


        texto_atraso = (
            "1 dia de atraso"
            if dias == 1
            else f"{dias} dias de atraso"
        )


        # HYDRA COBRA CLIENTE

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
                f"Olá, *{cliente_nome}*! Tudo bem? 😊\n\n"

                f"Verificamos que {origem}, "
                f"no dia *{data_retirada}*, "
                f"com saldo pendente de "
                f"*R$ {valor_formatado}*, "
                f"ainda consta em aberto conosco.\n\n"

                f"O vencimento foi em "
                f"*{data_vencimento}* e atualmente "
                f"está com *{texto_atraso}*.\n\n"

                f"Poderia confirmar para nós se esse "
                f"pagamento já foi realizado? "
                f"Obrigado! 😊"
            )


        # PISCINEIRO RESPONSÁVEL

        if (
            notinha.responsavel_cobranca
            == "PISCINEIRO"
        ):

            if not piscineiro_nome:
                return None


            return (
                f"Olá, *{piscineiro_nome}*! Tudo bem? 😊\n\n"

                f"Verificamos que a notinha do seu cliente "
                f"*{cliente_nome}*, retirada no dia "
                f"*{data_retirada}*, com saldo pendente de "
                f"*R$ {valor_formatado}*, ainda consta "
                f"em aberto conosco.\n\n"

                f"O vencimento foi em "
                f"*{data_vencimento}* e atualmente "
                f"está com *{texto_atraso}*.\n\n"

                f"Poderia verificar para nós se esse "
                f"pagamento já foi realizado? "
                f"Obrigado! 😊"
            )


        return None


    # =====================================================
    # MENSAGEM DE LEMBRETE
    # =====================================================

    @staticmethod
    def mensagem_lembrete(notinha):

        if not notinha:

            raise ValueError(
                "Notinha não encontrada."
            )


        saldo = (
            NotinhaService.saldo_pendente(
                notinha
            )
        )


        if saldo <= 0:
            return None


        hoje = date.today()


        dias_restantes = (
            notinha.data_vencimento
            - hoje
        ).days


        # Já venceu:
        # usa mensagem_cobranca(), não lembrete.
        if dias_restantes < 0:
            return None


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


        data_retirada = (
            notinha.data_retirada
            .strftime("%d/%m/%Y")
        )


        data_vencimento = (
            notinha.data_vencimento
            .strftime("%d/%m/%Y")
        )


        valor_formatado = (
            f"{saldo:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )


        if dias_restantes == 0:

            texto_prazo = (
                "vence *hoje*"
            )

        elif dias_restantes == 1:

            texto_prazo = (
                "vence *amanhã*"
            )

        else:

            texto_prazo = (
                f"vence em *{dias_restantes} dias*"
            )


        # HYDRA LEMBRA CLIENTE

        if (
            notinha.responsavel_cobranca
            == "HYDRA"
        ):

            if piscineiro_nome:

                origem = (
                    f"retirada pelo "
                    f"*{piscineiro_nome}*"
                )

            else:

                origem = (
                    "retirada diretamente "
                    "na Hydra"
                )


            return (
                f"Olá, *{cliente_nome}*! Tudo bem? 😊\n\n"

                f"Passando apenas para lembrar que "
                f"a notinha {origem}, no dia "
                f"*{data_retirada}*, possui saldo de "
                f"*R$ {valor_formatado}*.\n\n"

                f"O vencimento é em "
                f"*{data_vencimento}* e "
                f"{texto_prazo}.\n\n"

                f"Qualquer dúvida, estamos "
                f"à disposição. 😊"
            )


        # PISCINEIRO RECEBE LEMBRETE

        if (
            notinha.responsavel_cobranca
            == "PISCINEIRO"
        ):

            if not piscineiro_nome:
                return None


            return (
                f"Olá, *{piscineiro_nome}*! Tudo bem? 😊\n\n"

                f"Passando para lembrar que a notinha "
                f"do seu cliente *{cliente_nome}*, "
                f"retirada no dia *{data_retirada}*, "
                f"possui saldo de "
                f"*R$ {valor_formatado}*.\n\n"

                f"O vencimento é em "
                f"*{data_vencimento}* e "
                f"{texto_prazo}.\n\n"

                f"Qualquer dúvida, estamos "
                f"à disposição. 😊"
            )


        return None