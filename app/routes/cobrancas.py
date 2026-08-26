# Hydra ERP
# Responsável por: disponibilizar a área de pendências
# e cobranças financeiras do sistema.

from flask import (
    Blueprint,
    render_template
)

from app.services.cobranca_service import CobrancaService


cobrancas_bp = Blueprint(
    "cobrancas",
    __name__,
    url_prefix="/cobrancas"
)


@cobrancas_bp.route("/")
def index():

    grupos = (
        CobrancaService
        .agrupar_por_responsavel()
    )

    proximas = (
        CobrancaService
        .agrupar_proximas()
    )

    resumo = (
        CobrancaService.resumo()
    )

    return render_template(
        "cobrancas/index.html",

        grupos=grupos,

        proximas=proximas,

        resumo=resumo
    )