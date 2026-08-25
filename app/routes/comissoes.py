# Hydra ERP
# Responsável por: disponibilizar a área de comissões
# e registrar retiradas dos piscineiros.

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


@comissoes_bp.route("/")
def index():

    dados = (
        ComissaoService.listar_piscineiros()
    )

    return render_template(
        "comissoes/index.html",
        dados=dados
    )


@comissoes_bp.route("/<int:piscineiro_id>")
def detalhes(piscineiro_id):

    piscineiro = Piscineiro.query.get_or_404(
        piscineiro_id
    )

    gerado = (
        ComissaoService.total_gerado(
            piscineiro_id
        )
    )

    retirado = (
        ComissaoService.total_retirado(
            piscineiro_id
        )
    )

    saldo = (
        ComissaoService.saldo_disponivel(
            piscineiro_id
        )
    )

    retiradas = (
        ComissaoService.listar_retiradas(
            piscineiro_id
        )
    )

    return render_template(
        "comissoes/detalhes.html",
        piscineiro=piscineiro,
        gerado=gerado,
        retirado=retirado,
        saldo=saldo,
        retiradas=retiradas
    )


@comissoes_bp.route(
    "/<int:piscineiro_id>/retirada",
    methods=["POST"]
)
def registrar_retirada(piscineiro_id):

    try:

        ComissaoService.registrar_retirada(
            piscineiro_id=piscineiro_id,
            valor=request.form.get("valor"),
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