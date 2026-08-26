# Hydra ERP
# Responsável por: registrar pagamentos das notinhas
# e atualizar automaticamente sua situação financeira.

from datetime import date
from decimal import Decimal, InvalidOperation

from app.extensions import db
from app.models.pagamento import Pagamento
from app.models.notinha import Notinha
from app.services.notinha_service import NotinhaService
from app.services.movimentacao_service import MovimentacaoService


class PagamentoService:

    @staticmethod
    def _converter_decimal(valor, campo):
        try:
            numero = Decimal(
                str(valor).replace(",", ".")
            )

            if numero <= 0:
                raise ValueError(
                    f"{campo} deve ser maior que zero."
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
    def registrar_pagamento(
        notinha_id,
        valor,
        data_pagamento=None,
        pago_por="CLIENTE",
        forma_pagamento=None,
        observacao=None
    ):

        notinha = db.session.get(
            Notinha,
            int(notinha_id)
        )

        if not notinha:
            raise ValueError(
                "Notinha não encontrada."
            )

        if notinha.status == "CANCELADA":
            raise ValueError(
                "Não é possível registrar pagamento em uma notinha cancelada."
            )

        if notinha.status == "PAGA":
            raise ValueError(
                "Esta notinha já está totalmente paga."
            )

        valor = PagamentoService._converter_decimal(
            valor,
            "Valor do pagamento"
        )

        saldo_atual = (
            NotinhaService.saldo_pendente(
                notinha
            )
        )

        if valor > saldo_atual:
            raise ValueError(
                f"O pagamento não pode ser maior que o saldo pendente de R$ {saldo_atual:.2f}."
            )

        pago_por = (
            pago_por or "CLIENTE"
        ).upper()

        if pago_por not in {
            "CLIENTE",
            "PISCINEIRO",
            "OUTRO"
        }:
            raise ValueError(
                "Responsável pelo pagamento inválido."
            )

        if data_pagamento is None:
            data_pagamento = date.today()

        pagamento = Pagamento(
            notinha_id=notinha.id,
            valor=valor,
            data_pagamento=data_pagamento,
            pago_por=pago_por,
            forma_pagamento=(
                forma_pagamento or ""
            ).strip() or None,
            observacao=(
                observacao or ""
            ).strip() or None
        )

        try:

            db.session.add(
                pagamento
            )

            db.session.flush()

            saldo_restante = (
                saldo_atual
                - valor
            )

            if saldo_restante == 0:
                notinha.status = "PAGA"

            else:
                notinha.status = "PARCIAL"

            db.session.commit()

            MovimentacaoService.registrar(
    tipo="PAGAMENTO",
    acao="CRIAR",
    descricao=(
        f"Pagamento de R$ {pagamento.valor:.2f} "
        f"registrado na Notinha #{notinha.id} "
        f"do cliente {notinha.cliente.nome}."
    ),
    entidade="NOTINHA",
    entidade_id=notinha.id
)

            return pagamento

        except Exception:

            db.session.rollback()

            raise