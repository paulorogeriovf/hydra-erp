# Hydra ERP
# Responsável por: concentrar as regras de negócio relacionadas
# à criação, consulta e situação financeira das notinhas.

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

    @staticmethod
    def buscar_por_id(notinha_id):
        return db.session.get(Notinha, notinha_id)

    @staticmethod
    def listar_notinhas():
        return (
            Notinha.query
            .order_by(Notinha.data_criacao.desc())
            .all()
        )

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
                "Não é possível criar uma notinha para um cliente inativo."
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
                "A data de vencimento não pode ser anterior à data da retirada."
            )


        # =========================
        # ITENS
        # =========================

        if not itens:
            raise ValueError(
                "A notinha precisa possuir pelo menos um produto."
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
        # a cobrança automaticamente fica com a Hydra.
        if (
            cliente.piscineiro_id is None
            and responsavel_cobranca == "PISCINEIRO"
        ):
            responsavel_cobranca = "HYDRA"


        # =========================
        # CRIAR NOTINHA
        # =========================

        notinha = Notinha(
            cliente_id=cliente.id,

            # Snapshot do piscineiro no momento da venda.
            # Se o cliente trocar de piscineiro depois,
            # esta notinha continua ligada ao antigo.
            piscineiro_id=cliente.piscineiro_id,

            data_retirada=data_retirada,

            data_vencimento=data_vencimento,

            valor_total=Decimal("0.00"),

            status="ABERTA",

            responsavel_cobranca=responsavel_cobranca,

            observacao=(
                observacao or ""
            ).strip() or None
        )

        try:

            db.session.add(notinha)

            # Gera o ID da notinha sem confirmar
            # definitivamente a transação.
            db.session.flush()

            valor_total = Decimal("0.00")


            # =========================
            # PROCESSAR PRODUTOS
            # =========================

            for item in itens:

                produto_id = item.get(
                    "produto_id"
                )

                if not produto_id:
                    raise ValueError(
                        "Produto inválido na notinha."
                    )


                # QUANTIDADE

                quantidade = (
                    NotinhaService._converter_decimal(
                        item.get("quantidade"),
                        "Quantidade"
                    )
                )

                if quantidade <= 0:
                    raise ValueError(
                        "A quantidade deve ser maior que zero."
                    )


                # PRODUTO

                produto = db.session.get(
                    Produto,
                    int(produto_id)
                )

                if not produto:
                    raise ValueError(
                        "Um dos produtos selecionados não existe."
                    )

                if not produto.ativo:
                    raise ValueError(
                        f"O produto '{produto.nome}' está inativo."
                    )


                # =========================
                # PREÇO
                # =========================

                preco_informado = item.get(
                    "preco_unitario"
                )

                if (
                    preco_informado is None
                    or str(preco_informado).strip() == ""
                ):

                    preco_unitario = Decimal(
                        str(produto.preco_normal)
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
                        "O preço unitário deve ser maior que zero."
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


                # Só existe comissão se:
                # - produto gerar comissão;
                # - possuir percentual configurado;
                # - a venda tiver piscineiro.
                if (
                    gera_comissao
                    and produto.percentual_comissao is not None
                    and cliente.piscineiro_id is not None
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
                    notinha_id=notinha.id,

                    produto_id=produto.id,

                    quantidade=quantidade,

                    preco_unitario=preco_unitario,

                    subtotal=subtotal,

                    # Snapshot do produto.
                    nome_produto=produto.nome,

                    marca_produto=produto.marca,

                    # Snapshot da comissão.
                    gera_comissao=gera_comissao,

                    percentual_comissao=(
                        percentual_comissao
                    ),

                    valor_comissao=(
                        valor_comissao
                    )
                )

                db.session.add(
                    item_notinha
                )

                valor_total += subtotal


            # =========================
            # TOTAL FINAL
            # =========================

            if valor_total <= 0:
                raise ValueError(
                    "O valor total da notinha deve ser maior que zero."
                )


            notinha.valor_total = (
                valor_total
            )


            # Confirma notinha + itens
            # juntos na mesma transação.
            db.session.commit()

            return notinha


        except Exception:

            # Se qualquer etapa falhar,
            # nada daquela notinha fica salvo.
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
            str(notinha.valor_total)
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
            return Decimal("0.00")

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

            if notinha.status == "PARCIAL":
                return "PARCIAL_VENCIDA"

            return "VENCIDA"

        if notinha.status == "PARCIAL":
            return "PARCIAL"

        return "ABERTA"