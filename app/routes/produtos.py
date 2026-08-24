# Hydra ERP
# Responsável por: disponibilizar as rotas relacionadas ao cadastro de produtos.

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


@produtos_bp.route("/")
def listar():
    produtos = ProdutoService.listar_produtos()

    return render_template(
        "produtos/lista.html",
        produtos=produtos
    )


@produtos_bp.route("/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":

        try:
            ProdutoService.criar_produto(
                nome=request.form.get("nome"),
                marca=request.form.get("marca"),
                categoria=request.form.get("categoria"),
                preco_normal=request.form.get("preco_normal"),
                preco_atacado=request.form.get("preco_atacado"),
                gera_comissao=request.form.get("gera_comissao") == "on",
                percentual_comissao=request.form.get("percentual_comissao"),
                observacao=request.form.get("observacao")
            )

            flash("Produto cadastrado com sucesso.", "success")

            return redirect(url_for("produtos.listar"))

        except ValueError as erro:
            flash(str(erro), "error")

    return render_template("produtos/novo.html")


@produtos_bp.route("/<int:produto_id>/editar", methods=["GET", "POST"])
def editar(produto_id):

    produto = ProdutoService.buscar_por_id(produto_id)

    if not produto:
        return "Produto não encontrado.", 404

    if request.method == "POST":

        try:
            ProdutoService.editar_produto(
                produto_id=produto_id,
                nome=request.form.get("nome"),
                marca=request.form.get("marca"),
                categoria=request.form.get("categoria"),
                preco_normal=request.form.get("preco_normal"),
                preco_atacado=request.form.get("preco_atacado"),
                gera_comissao=request.form.get("gera_comissao") == "on",
                percentual_comissao=request.form.get("percentual_comissao"),
                observacao=request.form.get("observacao")
            )

            flash("Produto atualizado com sucesso.", "success")

            return redirect(url_for("produtos.listar"))

        except ValueError as erro:
            flash(str(erro), "error")

    return render_template(
        "produtos/editar.html",
        produto=produto
    )


@produtos_bp.route("/<int:produto_id>/status", methods=["POST"])
def alterar_status(produto_id):

    try:
        ProdutoService.alternar_status(produto_id)

        flash("Status do produto atualizado.", "success")

    except ValueError as erro:
        flash(str(erro), "error")

    return redirect(url_for("produtos.listar"))