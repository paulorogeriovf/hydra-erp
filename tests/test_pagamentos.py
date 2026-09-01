from decimal import Decimal

import pytest

from app.extensions import db
from app.services.notinha_service import NotinhaService
from app.services.pagamento_service import PagamentoService


# =========================================================
# 1. PAGAMENTO PARCIAL
# =========================================================

def test_pagamento_parcial(
    app,
    criar_notinha
):

    notinha = criar_notinha(
        "500.00"
    )


    PagamentoService.registrar_pagamento(
        notinha_id=notinha.id,
        valor="200.00",
        pago_por="CLIENTE",
        forma_pagamento="PIX"
    )


    db.session.refresh(
        notinha
    )


    assert NotinhaService.total_pago(
        notinha
    ) == Decimal("200.00")

    assert NotinhaService.saldo_pendente(
        notinha
    ) == Decimal("300.00")

    assert notinha.status == "PARCIAL"


# =========================================================
# 2. PAGAMENTO TOTAL
# =========================================================

def test_pagamento_total(
    app,
    criar_notinha
):

    notinha = criar_notinha(
        "500.00"
    )


    PagamentoService.registrar_pagamento(
        notinha_id=notinha.id,
        valor="500.00",
        pago_por="CLIENTE",
        forma_pagamento="PIX"
    )


    db.session.refresh(
        notinha
    )


    assert NotinhaService.total_pago(
        notinha
    ) == Decimal("500.00")

    assert NotinhaService.saldo_pendente(
        notinha
    ) == Decimal("0.00")

    assert notinha.status == "PAGA"


# =========================================================
# 3. PAGAMENTO MAIOR QUE O SALDO
# =========================================================

def test_pagamento_maior_que_saldo(
    app,
    criar_notinha
):

    notinha = criar_notinha(
        "500.00"
    )


    with pytest.raises(
        ValueError,
        match="pagamento não pode ser maior"
    ):

        PagamentoService.registrar_pagamento(
            notinha_id=notinha.id,
            valor="600.00"
        )


    assert NotinhaService.total_pago(
        notinha
    ) == Decimal("0.00")

    assert NotinhaService.saldo_pendente(
        notinha
    ) == Decimal("500.00")

    assert notinha.status == "ABERTA"


# =========================================================
# 4. PAGAMENTO EM NOTINHA PAGA
# =========================================================

def test_pagamento_em_notinha_paga(
    app,
    criar_notinha
):

    notinha = criar_notinha(
        "500.00"
    )


    PagamentoService.registrar_pagamento(
        notinha_id=notinha.id,
        valor="500.00"
    )


    db.session.refresh(
        notinha
    )


    assert notinha.status == "PAGA"


    with pytest.raises(
        ValueError,
        match="já está totalmente paga"
    ):

        PagamentoService.registrar_pagamento(
            notinha_id=notinha.id,
            valor="100.00"
        )


    assert NotinhaService.total_pago(
        notinha
    ) == Decimal("500.00")

    assert NotinhaService.saldo_pendente(
        notinha
    ) == Decimal("0.00")