# Hydra ERP
# Responsável por: disponibilizar as rotas relacionadas
# ao cadastro, busca e gerenciamento de produtos.

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from app.services.produto_service import ProdutoService


produtos_bp = Blueprint(
    "produtos",
    __name__,
    url_prefix="/produtos"
)


# =========================================================
# LISTAGEM / BUSCA
# =========================================================

@produtos_bp.route("/")
def listar():

    busca = (
        request.args.get(
            "busca",
            ""
        )
        .strip()
    )

    todos_produtos = (
        ProdutoService.listar_produtos()
    )


    if busca:

        busca_lower = busca.lower()

        produtos = []


        for produto in todos_produtos:

            nome = (
                produto.nome.lower()
                if produto.nome
                else ""
            )

            marca = (
                produto.marca.lower()
                if produto.marca
                else ""
            )


            if (
                busca_lower in nome
                or busca_lower in marca
            ):

                produtos.append(
                    produto
                )

    else:

        produtos = todos_produtos


    return render_template(
        "produtos/lista.html",

        produtos=
            produtos,

        todos_produtos=
            todos_produtos,

        busca=
            busca
    )


# =========================================================
# NOVO PRODUTO
# =========================================================

@produtos_bp.route(
    "/novo",
    methods=["GET", "POST"]
)
def novo():

    if request.method == "POST":

        try:

            ProdutoService.criar_produto(

                nome=
                    request.form.get(
                        "nome"
                    ),

                marca=
                    request.form.get(
                        "marca"
                    ),

                categoria=
                    request.form.get(
                        "categoria"
                    ),

                preco_normal=
                    request.form.get(
                        "preco_normal"
                    ),

                preco_atacado=
                    request.form.get(
                        "preco_atacado"
                    ),

                gera_comissao=
                    request.form.get(
                        "gera_comissao"
                    )
                    == "on",

                percentual_comissao=
                    request.form.get(
                        "percentual_comissao"
                    ),

                observacao=
                    request.form.get(
                        "observacao"
                    )
            )


            flash(
                "Produto cadastrado com sucesso.",
                "success"
            )


            return redirect(
                url_for(
                    "produtos.listar"
                )
            )


        except ValueError as erro:

            flash(
                str(erro),
                "error"
            )


    return render_template(
        "produtos/novo.html"
    )


# =========================================================
# EDITAR PRODUTO
# =========================================================

@produtos_bp.route(
    "/<int:produto_id>/editar",
    methods=["GET", "POST"]
)
def editar(produto_id):

    produto = (
        ProdutoService.buscar_por_id(
            produto_id
        )
    )


    if not produto:

        return (
            "Produto não encontrado.",
            404
        )


    if request.method == "POST":

        try:

            ProdutoService.editar_produto(

                produto_id=
                    produto_id,

                nome=
                    request.form.get(
                        "nome"
                    ),

                marca=
                    request.form.get(
                        "marca"
                    ),

                categoria=
                    request.form.get(
                        "categoria"
                    ),

                preco_normal=
                    request.form.get(
                        "preco_normal"
                    ),

                preco_atacado=
                    request.form.get(
                        "preco_atacado"
                    ),

                gera_comissao=
                    request.form.get(
                        "gera_comissao"
                    )
                    == "on",

                percentual_comissao=
                    request.form.get(
                        "percentual_comissao"
                    ),

                observacao=
                    request.form.get(
                        "observacao"
                    )
            )


            flash(
                "Produto atualizado com sucesso.",
                "success"
            )


            return redirect(
                url_for(
                    "produtos.listar"
                )
            )


        except ValueError as erro:

            flash(
                str(erro),
                "error"
            )


    return render_template(
        "produtos/editar.html",
        produto=produto
    )


# =========================================================
# ALTERAR STATUS
# =========================================================

@produtos_bp.route(
    "/<int:produto_id>/status",
    methods=["POST"]
)
def alterar_status(produto_id):

    try:

        ProdutoService.alternar_status(
            produto_id
        )


        flash(
            "Status do produto atualizado.",
            "success"
        )


    except ValueError as erro:

        flash(
            str(erro),
            "error"
        )


    return redirect(
        url_for(
            "produtos.listar"
        )
    )