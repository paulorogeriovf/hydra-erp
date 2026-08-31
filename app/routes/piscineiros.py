# Hydra ERP
# Responsável por: disponibilizar as rotas de cadastro,
# busca e gerenciamento de piscineiros.

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from app.services.piscineiro_service import PiscineiroService


piscineiros_bp = Blueprint(
    "piscineiros",
    __name__,
    url_prefix="/piscineiros"
)


# =========================================================
# LISTAGEM / BUSCA
# =========================================================

@piscineiros_bp.route("/")
def listar():

    busca = (
        request.args.get(
            "busca",
            ""
        )
        .strip()
    )

    todos_piscineiros = (
        PiscineiroService.listar_piscineiros()
    )


    if busca:

        busca_lower = busca.lower()

        piscineiros = [
            piscineiro
            for piscineiro in todos_piscineiros

            if (
                piscineiro.nome
                and busca_lower
                in piscineiro.nome.lower()
            )
        ]

    else:

        piscineiros = todos_piscineiros


    return render_template(
        "piscineiros/lista.html",

        piscineiros=
            piscineiros,

        todos_piscineiros=
            todos_piscineiros,

        busca=
            busca
    )


# =========================================================
# NOVO PISCINEIRO
# =========================================================

@piscineiros_bp.route(
    "/novo",
    methods=["GET", "POST"]
)
def novo():

    if request.method == "POST":

        try:

            PiscineiroService.criar_piscineiro(

                nome=
                    request.form.get(
                        "nome"
                    ),

                telefone=
                    request.form.get(
                        "telefone"
                    ),

                whatsapp=
                    request.form.get(
                        "whatsapp"
                    ),

                cidade=
                    request.form.get(
                        "cidade"
                    ),

                endereco=
                    request.form.get(
                        "endereco"
                    ),

                observacao=
                    request.form.get(
                        "observacao"
                    )
            )


            flash(
                "Piscineiro cadastrado com sucesso.",
                "success"
            )


            return redirect(
                url_for(
                    "piscineiros.listar"
                )
            )


        except ValueError as erro:

            flash(
                str(erro),
                "error"
            )


    return render_template(
        "piscineiros/novo.html"
    )


# =========================================================
# EDITAR PISCINEIRO
# =========================================================

@piscineiros_bp.route(
    "/<int:piscineiro_id>/editar",
    methods=["GET", "POST"]
)
def editar(piscineiro_id):

    piscineiro = (
        PiscineiroService.buscar_por_id(
            piscineiro_id
        )
    )


    if not piscineiro:

        return (
            "Piscineiro não encontrado.",
            404
        )


    if request.method == "POST":

        try:

            PiscineiroService.editar_piscineiro(

                piscineiro_id=
                    piscineiro_id,

                nome=
                    request.form.get(
                        "nome"
                    ),

                telefone=
                    request.form.get(
                        "telefone"
                    ),

                whatsapp=
                    request.form.get(
                        "whatsapp"
                    ),

                cidade=
                    request.form.get(
                        "cidade"
                    ),

                endereco=
                    request.form.get(
                        "endereco"
                    ),

                observacao=
                    request.form.get(
                        "observacao"
                    )
            )


            flash(
                "Piscineiro atualizado com sucesso.",
                "success"
            )


            return redirect(
                url_for(
                    "piscineiros.listar"
                )
            )


        except ValueError as erro:

            flash(
                str(erro),
                "error"
            )


    return render_template(
        "piscineiros/editar.html",
        piscineiro=piscineiro
    )


# =========================================================
# ALTERAR STATUS
# =========================================================

@piscineiros_bp.route(
    "/<int:piscineiro_id>/status",
    methods=["POST"]
)
def alterar_status(piscineiro_id):

    try:

        PiscineiroService.alternar_status(
            piscineiro_id
        )


        flash(
            "Status do piscineiro atualizado.",
            "success"
        )


    except ValueError as erro:

        flash(
            str(erro),
            "error"
        )


    return redirect(
        url_for(
            "piscineiros.listar"
        )
    )


# =========================================================
# DETALHES
# =========================================================

@piscineiros_bp.route(
    "/<int:piscineiro_id>"
)
def detalhes(piscineiro_id):

    piscineiro = (
        PiscineiroService.buscar_por_id(
            piscineiro_id
        )
    )


    if not piscineiro:

        return (
            "Piscineiro não encontrado.",
            404
        )


    resumo = (
        PiscineiroService.resumo_financeiro(
            piscineiro_id
        )
    )


    produtos_mais_vendidos = (
        PiscineiroService
        .produtos_mais_vendidos(
            piscineiro_id
        )
    )


    grafico_vendas = (
        PiscineiroService
        .vendas_ultimos_meses(
            piscineiro_id
        )
    )


    clientes_atuais = sorted(
        piscineiro.clientes,
        key=lambda cliente:
            cliente.nome.lower()
    )


    return render_template(
        "piscineiros/detalhes.html",

        piscineiro=
            piscineiro,

        clientes=
            clientes_atuais,

        resumo=
            resumo,

        produtos_mais_vendidos=
            produtos_mais_vendidos,

        grafico_vendas=
            grafico_vendas
    )