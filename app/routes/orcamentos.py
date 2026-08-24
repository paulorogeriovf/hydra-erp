# Hydra ERP
# Responsável por: disponibilizar o gerador de orçamentos
# utilizando os produtos ativos cadastrados no ERP.

from flask import Blueprint, render_template, jsonify

from app.models.produto import Produto


orcamentos_bp = Blueprint(
    "orcamentos",
    __name__,
    url_prefix="/orcamentos"
)


@orcamentos_bp.route("/")
def index():
    return render_template("orcamentos/index.html")


@orcamentos_bp.route("/api/produtos")
def api_produtos():

    produtos = (
        Produto.query
        .filter_by(ativo=True)
        .order_by(
            Produto.categoria.asc(),
            Produto.nome.asc()
        )
        .all()
    )

    resultado = []

    for produto in produtos:

        resultado.append({
            "id": produto.id,
            "nome": produto.nome,
            "marca": produto.marca,
            "categoria": produto.categoria or "Outros",
            "preco": float(produto.preco_normal)
        })

    return jsonify(resultado)