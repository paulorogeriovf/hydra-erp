from datetime import date, timedelta
from decimal import Decimal

from app.extensions import db

from app.models.cliente import Cliente
from app.models.piscineiro import Piscineiro
from app.models.produto import Produto

from app.services.notinha_service import NotinhaService
from app.services.cliente_service import ClienteService


# =========================================================
# HISTÓRICO DE TROCA DE PISCINEIRO
# =========================================================

def test_troca_piscineiro_preserva_notinha_antiga(app):

    # =====================================================
    # CRIAR DOIS PISCINEIROS
    # =====================================================

    piscineiro_antigo = Piscineiro(
        nome="Piscineiro Antigo Pytest",
        ativo=True
    )

    piscineiro_novo = Piscineiro(
        nome="Piscineiro Novo Pytest",
        ativo=True
    )

    db.session.add_all([
        piscineiro_antigo,
        piscineiro_novo
    ])

    db.session.flush()


    # =====================================================
    # CLIENTE COMEÇA COM O PISCINEIRO ANTIGO
    # =====================================================

    cliente = Cliente(
        nome="Cliente Histórico Pytest",
        piscineiro_id=piscineiro_antigo.id,
        ativo=True
    )

    db.session.add(cliente)


    # =====================================================
    # PRODUTO
    # =====================================================

    produto = Produto(
        nome="Produto Histórico Pytest",
        marca="Teste",
        categoria="Teste",
        preco_normal=Decimal("500.00"),
        gera_comissao=False,
        ativo=True
    )

    db.session.add(produto)

    db.session.commit()


    # Guardamos os IDs para facilitar as verificações
    id_piscineiro_antigo = piscineiro_antigo.id
    id_piscineiro_novo = piscineiro_novo.id


    # =====================================================
    # CRIAR NOTINHA ENQUANTO CLIENTE ESTÁ NO ANTIGO
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
                "preco_unitario": "500.00"
            }
        ],
        responsavel_cobranca="PISCINEIRO"
    )


    # A notinha nasceu vinculada ao piscineiro antigo
    assert (
        notinha.piscineiro_id
        == id_piscineiro_antigo
    )


    # =====================================================
    # TRANSFERIR CLIENTE PARA OUTRO PISCINEIRO
    # =====================================================

    ClienteService.mudar_piscineiro(
        cliente_id=cliente.id,
        novo_piscineiro_id=id_piscineiro_novo,
        observacao="Transferência teste pytest"
    )


    db.session.refresh(cliente)
    db.session.refresh(notinha)


    # =====================================================
    # 1. CLIENTE AGORA PERTENCE AO NOVO
    # =====================================================

    assert (
        cliente.piscineiro_id
        == id_piscineiro_novo
    )


    # =====================================================
    # 2. NOTINHA ANTIGA CONTINUA NO ANTIGO
    # =====================================================

    assert (
        notinha.piscineiro_id
        == id_piscineiro_antigo
    )


    # =====================================================
    # 3. HISTÓRICO DA TRANSFERÊNCIA FOI CRIADO
    # =====================================================

    historico = (
        ClienteService.historico_piscineiros(
            cliente.id
        )
    )


    assert len(historico) == 1

    assert (
        historico[0].piscineiro_anterior_id
        == id_piscineiro_antigo
    )

    assert (
        historico[0].piscineiro_novo_id
        == id_piscineiro_novo
    )

    assert (
        historico[0].observacao
        == "Transferência teste pytest"
    )