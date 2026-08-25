# Hydra ERP
# Responsável por: disponibilizar as rotas de criação,
# consulta e gerenciamento das notinhas.

from datetime import date, timedelta
from app.services.pagamento_service import PagamentoService

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
    current_app
)

from app.services.notinha_service import NotinhaService
from app.services.cliente_service import ClienteService
from app.services.produto_service import ProdutoService
from app.services.observacao_notinha_service import ObservacaoNotinhaService
from app.services.anexo_notinha_service import AnexoNotinhaService


notinhas_bp = Blueprint(
    "notinhas",
    __name__,
    url_prefix="/notinhas"
)


@notinhas_bp.route("/")
def listar():

    notinhas = NotinhaService.listar_notinhas()

    dados_notinhas = []

    for notinha in notinhas:

        dados_notinhas.append({
            "notinha": notinha,
            "total_pago": NotinhaService.total_pago(notinha),
            "saldo": NotinhaService.saldo_pendente(notinha),
            "situacao": NotinhaService.situacao(notinha)
        })

    return render_template(
        "notinhas/lista.html",
        dados_notinhas=dados_notinhas
    )


@notinhas_bp.route("/nova", methods=["GET", "POST"])
def nova():

    clientes = [
        cliente
        for cliente in ClienteService.listar_clientes()
        if cliente.ativo
    ]

    produtos = [
        produto
        for produto in ProdutoService.listar_produtos()
        if produto.ativo
    ]

    if request.method == "POST":

        try:

            produto_ids = request.form.getlist(
                "produto_id[]"
            )

            quantidades = request.form.getlist(
                "quantidade[]"
            )

            precos = request.form.getlist(
                "preco_unitario[]"
            )

            itens = []

            for produto_id, quantidade, preco in zip(
                produto_ids,
                quantidades,
                precos
            ):

                if not produto_id:
                    continue

                itens.append({
                    "produto_id": produto_id,
                    "quantidade": quantidade,
                    "preco_unitario": preco
                })

            NotinhaService.criar_notinha(
                cliente_id=request.form.get(
                    "cliente_id"
                ),

                data_retirada=date.fromisoformat(
                    request.form.get(
                        "data_retirada"
                    )
                ),

                data_vencimento=date.fromisoformat(
                    request.form.get(
                        "data_vencimento"
                    )
                ),

                itens=itens,

                responsavel_cobranca=request.form.get(
                    "responsavel_cobranca"
                ),

                observacao=request.form.get(
                    "observacao"
                )
            )

            flash(
                "Notinha cadastrada com sucesso.",
                "success"
            )

            return redirect(
                url_for("notinhas.listar")
            )

        except (
            ValueError,
            TypeError
        ) as erro:

            flash(
                str(erro),
                "error"
            )

    return render_template(
        "notinhas/nova.html",
        clientes=clientes,
        produtos=produtos,
        hoje=date.today().isoformat(),
        vencimento_padrao=(
            date.today()
            + timedelta(days=30)
        ).isoformat()
    )


@notinhas_bp.route("/<int:notinha_id>")
def detalhes(notinha_id):

    notinha = NotinhaService.buscar_por_id(
        notinha_id
    )

    if not notinha:
        return "Notinha não encontrada.", 404

    return render_template(
    "notinhas/detalhes.html",

    notinha=notinha,

    total_pago=NotinhaService.total_pago(
        notinha
    ),

    saldo=NotinhaService.saldo_pendente(
        notinha
    ),

    situacao=NotinhaService.situacao(
        notinha
    ),

    hoje=date.today().isoformat()
)

@notinhas_bp.route(
    "/<int:notinha_id>/pagamento",
    methods=["POST"]
)
def registrar_pagamento(notinha_id):

    try:

        PagamentoService.registrar_pagamento(
            notinha_id=notinha_id,
            valor=request.form.get("valor"),
            data_pagamento=date.fromisoformat(
                request.form.get("data_pagamento")
            ),
            pago_por=request.form.get("pago_por"),
            forma_pagamento=request.form.get(
                "forma_pagamento"
            ),
            observacao=request.form.get(
                "observacao"
            )
        )

        flash(
            "Pagamento registrado com sucesso.",
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
            "notinhas.detalhes",
            notinha_id=notinha_id
        )
    )

# =========================================================
# OBSERVAÇÕES
# =========================================================

@notinhas_bp.route(
    "/<int:notinha_id>/observacao",
    methods=["POST"]
)
def adicionar_observacao(notinha_id):

    try:

        ObservacaoNotinhaService.adicionar(
            notinha_id=notinha_id,
            texto=request.form.get("texto")
        )

        flash(
            "Observação adicionada com sucesso.",
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
            "notinhas.detalhes",
            notinha_id=notinha_id
        )
    )


# =========================================================
# ANEXOS
# =========================================================

@notinhas_bp.route(
    "/<int:notinha_id>/anexo",
    methods=["POST"]
)
def adicionar_anexo(notinha_id):

    try:

        arquivo = request.files.get(
            "arquivo"
        )

        AnexoNotinhaService.salvar(
            notinha_id=notinha_id,

            arquivo=arquivo,

            tipo=request.form.get(
                "tipo"
            ),

            pagamento_id=request.form.get(
                "pagamento_id"
            ) or None,

            observacao=request.form.get(
                "observacao"
            )
        )

        flash(
            "Arquivo anexado com sucesso.",
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
            "notinhas.detalhes",
            notinha_id=notinha_id
        )
    )

@notinhas_bp.route(
    "/anexos/<path:caminho>"
)
def visualizar_anexo(caminho):

    return send_from_directory(
        current_app.config[
            "UPLOAD_FOLDER"
        ],
        caminho
    )