from datetime import date, timedelta
from decimal import Decimal

from app.extensions import db
from app.services.notinha_service import NotinhaService
from app.services.pagamento_service import PagamentoService


# =========================================================
# 1. NOTINHA VENCIDA
# =========================================================

def test_notinha_vencida(
    app,
    criar_notinha
):

    notinha = criar_notinha(
        valor="500.00",
        vencimento=(
            date.today()
            - timedelta(days=5)
        )
    )


    assert NotinhaService.saldo_pendente(
        notinha
    ) == Decimal("500.00")

    assert (
        NotinhaService.esta_vencida(
            notinha
        )
        is True
    )

    assert (
        NotinhaService.situacao(
            notinha
        )
        == "VENCIDA"
    )

    assert (
        NotinhaService.dias_atraso(
            notinha
        )
        == 5
    )


# =========================================================
# 2. NOTINHA PARCIAL E VENCIDA
# =========================================================

def test_notinha_parcial_vencida(
    app,
    criar_notinha
):

    notinha = criar_notinha(
        valor="500.00",
        vencimento=(
            date.today()
            - timedelta(days=10)
        )
    )


    PagamentoService.registrar_pagamento(
        notinha_id=notinha.id,
        valor="200.00"
    )


    db.session.refresh(
        notinha
    )


    assert notinha.status == "PARCIAL"

    assert NotinhaService.saldo_pendente(
        notinha
    ) == Decimal("300.00")

    assert (
        NotinhaService.esta_vencida(
            notinha
        )
        is True
    )

    assert (
        NotinhaService.situacao(
            notinha
        )
        == "PARCIAL_VENCIDA"
    )

    assert (
        NotinhaService.dias_atraso(
            notinha
        )
        == 10
    )


# =========================================================
# 3. NOTINHA PAGA NÃO É VENCIDA
# =========================================================

def test_notinha_paga_nao_e_vencida(
    app,
    criar_notinha
):

    notinha = criar_notinha(
        valor="500.00",
        vencimento=(
            date.today()
            - timedelta(days=20)
        )
    )


    PagamentoService.registrar_pagamento(
        notinha_id=notinha.id,
        valor="500.00"
    )


    db.session.refresh(
        notinha
    )


    assert notinha.status == "PAGA"

    assert NotinhaService.saldo_pendente(
        notinha
    ) == Decimal("0.00")

    assert (
        NotinhaService.esta_vencida(
            notinha
        )
        is False
    )

    assert (
        NotinhaService.situacao(
            notinha
        )
        == "PAGA"
    )

    assert (
        NotinhaService.dias_atraso(
            notinha
        )
        == 0
    )