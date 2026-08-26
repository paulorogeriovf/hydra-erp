# Hydra ERP
# Responsável por: disponibilizar a área
# de inteligência comercial e análise de vendas.

from flask import (
    Blueprint,
    render_template,
    request
)

from app.services.inteligencia_vendas_service import (
    InteligenciaVendasService
)


inteligencia_vendas_bp = Blueprint(
    "inteligencia_vendas",
    __name__,
    url_prefix="/inteligencia-vendas"
)


# =========================================================
# PÁGINA PRINCIPAL
# =========================================================

@inteligencia_vendas_bp.route("/")
def index():

    resumo = (
        InteligenciaVendasService
        .resumo_geral()
    )


    # TOP 5 NA PÁGINA PRINCIPAL

    produtos = (
        InteligenciaVendasService
        .ranking_produtos(
            limite=5
        )
    )


    clientes = (
        InteligenciaVendasService
        .ranking_clientes(
            limite=5
        )
    )


    piscineiros = (
        InteligenciaVendasService
        .ranking_piscineiros(
            limite=5
        )
    )

    return render_template(
        "inteligencia_vendas/index.html",

        resumo=
            resumo,

        produtos=
            produtos,

        clientes=
            clientes,

        piscineiros=
            piscineiros,
    )


# =========================================================
# RANKING COMPLETO DE CLIENTES
# =========================================================

@inteligencia_vendas_bp.route(
    "/clientes"
)
def ranking_clientes():

    clientes = (
        InteligenciaVendasService
        .ranking_clientes(
            limite=1000
        )
    )


    return render_template(
        "inteligencia_vendas/clientes.html",
        clientes=clientes
    )


# =========================================================
# RANKING COMPLETO DE PRODUTOS
# =========================================================

@inteligencia_vendas_bp.route(
    "/produtos"
)
def ranking_produtos():

    produtos = (
        InteligenciaVendasService
        .ranking_produtos(
            limite=1000
        )
    )


    return render_template(
        "inteligencia_vendas/produtos.html",
        produtos=produtos
    )


# =========================================================
# RANKING COMPLETO DE PISCINEIROS
# =========================================================

@inteligencia_vendas_bp.route(
    "/piscineiros"
)
def ranking_piscineiros():

    piscineiros = (
        InteligenciaVendasService
        .ranking_piscineiros(
            limite=1000
        )
    )


    return render_template(
        "inteligencia_vendas/piscineiros.html",
        piscineiros=piscineiros
    )

# =========================================================
# OPORTUNIDADES DE VENDAS
# =========================================================

@inteligencia_vendas_bp.route(
    "/oportunidades"
)
def oportunidades():

    nivel = (
        request.args.get(
            "nivel",
            ""
        )
        .strip()
        .upper()
    )


    oportunidades_produtos = (
        InteligenciaVendasService
        .oportunidades_produtos()
    )


    clientes_risco = (
        InteligenciaVendasService
        .clientes_em_risco()
    )


    if nivel in {
        "ALTA",
        "ATENCAO"
    }:

        oportunidades_produtos = [
            item
            for item
            in oportunidades_produtos
            if item["nivel"] == nivel
        ]


        clientes_risco = [
            item
            for item
            in clientes_risco
            if item["nivel"] == nivel
        ]


    return render_template(
        "inteligencia_vendas/oportunidades.html",

        oportunidades=
            oportunidades_produtos,

        clientes_risco=
            clientes_risco,

        nivel_filtro=
            nivel
    )