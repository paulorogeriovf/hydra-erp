# Hydra ERP
# Responsável por: disponibilizar a área de comissões,
# exibir a origem dos valores e registrar retiradas
# dos piscineiros.

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from app.services.comissao_service import ComissaoService
from app.models.piscineiro import Piscineiro


comissoes_bp = Blueprint(
    "comissoes",
    __name__,
    url_prefix="/comissoes"
)


# =========================================================
# LISTAGEM GERAL DE COMISSÕES
# =========================================================

@comissoes_bp.route("/")
def index():

    dados = (
        ComissaoService.listar_piscineiros()
    )

    return render_template(
        "comissoes/index.html",
        dados=dados
    )


# =========================================================
# DETALHES DA COMISSÃO DE UM PISCINEIRO
# =========================================================

@comissoes_bp.route("/<int:piscineiro_id>")
def detalhes(piscineiro_id):

    piscineiro = Piscineiro.query.get_or_404(
        piscineiro_id
    )

    # Total de comissão gerada pelas vendas.
    gerado = (
        ComissaoService.total_gerado(
            piscineiro_id
        )
    )

    # Total que o piscineiro já retirou.
    retirado = (
        ComissaoService.total_retirado(
            piscineiro_id
        )
    )

    # Saldo ainda disponível para retirada.
    saldo = (
        ComissaoService.saldo_disponivel(
            piscineiro_id
        )
    )

    # Histórico de retiradas realizadas.
    retiradas = (
        ComissaoService.listar_retiradas(
            piscineiro_id
        )
    )

    # Produtos/notinhas que deram origem
    # às comissões do piscineiro.
    origens = (
        ComissaoService.listar_origens(
            piscineiro_id
        )
    )

    return render_template(
        "comissoes/detalhes.html",
        piscineiro=piscineiro,
        gerado=gerado,
        retirado=retirado,
        saldo=saldo,
        retiradas=retiradas,
        origens=origens
    )


# =========================================================
# REGISTRAR RETIRADA DE COMISSÃO
# =========================================================

@comissoes_bp.route(
    "/<int:piscineiro_id>/retirada",
    methods=["POST"]
)
def registrar_retirada(piscineiro_id):

    try:

        ComissaoService.registrar_retirada(
            piscineiro_id=piscineiro_id,
            valor=request.form.get(
                "valor"
            ),
            observacao=request.form.get(
                "observacao"
            )
        )

        flash(
            "Retirada registrada com sucesso.",
            "success"
        )

    except (
        ValueError,
        TypeError
    ) as erro:

        flash(
            str(erro),
            "error"
        )

    return redirect(
        url_for(
            "comissoes.detalhes",
            piscineiro_id=piscineiro_id
        )
    )