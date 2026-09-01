from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.extensions import db
from app.models.cliente import Cliente
from app.models.piscineiro import Piscineiro
from app.models.produto import Produto
from app.services.notinha_service import NotinhaService
from app.services.comissao_service import ComissaoService


# =========================================================
# AUXILIAR
# =========================================================

def criar_cenario_comissao(
    gera_comissao=True,
    percentual="5.00",
    valor_produto="1000.00"
):

    # =====================================================
    # PISCINEIRO
    # =====================================================

    piscineiro = Piscineiro(
        nome="Piscineiro Teste Pytest",
        ativo=True
    )

    db.session.add(
        piscineiro
    )

    db.session.flush()


    # =====================================================
    # CLIENTE VINCULADO AO PISCINEIRO
    # =====================================================

    cliente = Cliente(
        nome="Cliente Comissão Pytest",
        piscineiro_id=piscineiro.id,
        ativo=True
    )

    db.session.add(
        cliente
    )


    # =====================================================
    # PRODUTO
    # =====================================================

    produto = Produto(
        nome="Produto Comissão Pytest",
        marca="Teste",
        categoria="Teste",
        preco_normal=Decimal(
            valor_produto
        ),
        gera_comissao=gera_comissao,
        percentual_comissao=(
            Decimal(percentual)
            if gera_comissao
            else None
        ),
        ativo=True
    )

    db.session.add(
        produto
    )

    db.session.commit()


    # =====================================================
    # NOTINHA
    # =====================================================

    notinha = NotinhaService.criar_notinha(
        cliente_id=cliente.id,
        data_retirada=date.today(),
        data_vencimento=(
            date.today()
            + timedelta(days=30)
        ),
        itens=[
            {
                "produto_id": produto.id,
                "quantidade": 1,
                "preco_unitario": valor_produto
            }
        ],
        responsavel_cobranca="PISCINEIRO"
    )


    return {
        "piscineiro": piscineiro,
        "cliente": cliente,
        "produto": produto,
        "notinha": notinha
    }


# =========================================================
# 1. PRODUTO COM COMISSÃO
# =========================================================

def test_calculo_comissao(
    app
):

    cenario = criar_cenario_comissao(
        gera_comissao=True,
        percentual="5.00",
        valor_produto="1000.00"
    )

    piscineiro = cenario[
        "piscineiro"
    ]


    # 5% de R$ 1.000 = R$ 50
    assert ComissaoService.total_gerado(
        piscineiro.id
    ) == Decimal("50.00")


    assert ComissaoService.saldo_disponivel(
        piscineiro.id
    ) == Decimal("50.00")


# =========================================================
# 2. PRODUTO SEM COMISSÃO
# =========================================================

def test_produto_sem_comissao(
    app
):

    cenario = criar_cenario_comissao(
        gera_comissao=False,
        valor_produto="1000.00"
    )

    piscineiro = cenario[
        "piscineiro"
    ]


    assert ComissaoService.total_gerado(
        piscineiro.id
    ) == Decimal("0.00")


    assert ComissaoService.saldo_disponivel(
        piscineiro.id
    ) == Decimal("0.00")


# =========================================================
# 3. RETIRADA PARCIAL DE COMISSÃO
# =========================================================

def test_retirada_parcial_comissao(
    app
):

    cenario = criar_cenario_comissao(
        gera_comissao=True,
        percentual="5.00",
        valor_produto="1000.00"
    )

    piscineiro = cenario[
        "piscineiro"
    ]


    # Comissão disponível inicialmente:
    # R$ 50
    assert ComissaoService.saldo_disponivel(
        piscineiro.id
    ) == Decimal("50.00")


    # Retira R$ 30
    ComissaoService.registrar_retirada(
        piscineiro_id=piscineiro.id,
        valor="30.00",
        observacao="Retirada teste pytest"
    )


    assert ComissaoService.total_gerado(
        piscineiro.id
    ) == Decimal("50.00")


    assert ComissaoService.total_retirado(
        piscineiro.id
    ) == Decimal("30.00")


    assert ComissaoService.saldo_disponivel(
        piscineiro.id
    ) == Decimal("20.00")


# =========================================================
# 4. RETIRADA MAIOR QUE O SALDO
# =========================================================

def test_retirada_maior_que_saldo(
    app
):

    cenario = criar_cenario_comissao(
        gera_comissao=True,
        percentual="5.00",
        valor_produto="1000.00"
    )

    piscineiro = cenario[
        "piscineiro"
    ]


    assert ComissaoService.saldo_disponivel(
        piscineiro.id
    ) == Decimal("50.00")


    # Tenta retirar R$ 60,
    # mas existem apenas R$ 50 disponíveis.
    with pytest.raises(
        ValueError,
        match="retirada não pode ser maior"
    ):

        ComissaoService.registrar_retirada(
            piscineiro_id=piscineiro.id,
            valor="60.00"
        )


    # Nenhuma retirada deve ter sido registrada.
    assert ComissaoService.total_retirado(
        piscineiro.id
    ) == Decimal("0.00")


    assert ComissaoService.saldo_disponivel(
        piscineiro.id
    ) == Decimal("50.00")