# Hydra ERP
# Responsável por: disponibilizar a área
# de histórico de movimentações do sistema.

from flask import (
    Blueprint,
    render_template,
    request
)

from app.services.movimentacao_service import MovimentacaoService


historico_bp = Blueprint(
    "historico",
    __name__,
    url_prefix="/historico"
)


@historico_bp.route("/")
def index():

    tipo = (
        request.args.get(
            "tipo",
            ""
        )
        .strip()
        .upper()
    )


    if tipo:

        movimentacoes = (
            MovimentacaoService
            .listar_por_tipo(
                tipo
            )
        )

    else:

        movimentacoes = (
            MovimentacaoService
            .listar()
        )


    return render_template(
        "historico/index.html",

        movimentacoes=
            movimentacoes,

        tipo_filtro=
            tipo
    )