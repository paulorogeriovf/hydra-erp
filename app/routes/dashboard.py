# Hydra ERP
# Responsável por: disponibilizar a página inicial e os indicadores gerais do sistema.

from flask import Blueprint, render_template

from app.models.produto import Produto
from app.models.piscineiro import Piscineiro
from app.models.cliente import Cliente


dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


@dashboard_bp.route("/")
def index():

    total_produtos = Produto.query.count()

    produtos_ativos = Produto.query.filter_by(
        ativo=True
    ).count()

    total_piscineiros = Piscineiro.query.count()

    piscineiros_ativos = Piscineiro.query.filter_by(
        ativo=True
    ).count()

    total_clientes = Cliente.query.count()

    clientes_ativos = Cliente.query.filter_by(
        ativo=True
    ).count()

    clientes_sem_piscineiro = Cliente.query.filter(
        Cliente.piscineiro_id.is_(None)
    ).count()

    return render_template(
        "dashboard/index.html",

        total_produtos=total_produtos,
        produtos_ativos=produtos_ativos,

        total_piscineiros=total_piscineiros,
        piscineiros_ativos=piscineiros_ativos,

        total_clientes=total_clientes,
        clientes_ativos=clientes_ativos,
        clientes_sem_piscineiro=clientes_sem_piscineiro
    )