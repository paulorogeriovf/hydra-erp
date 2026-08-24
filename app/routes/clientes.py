# Hydra ERP
# Responsável por: disponibilizar as rotas de cadastro, edição e vínculo de clientes.

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from app.services.cliente_service import ClienteService
from app.services.piscineiro_service import PiscineiroService


clientes_bp = Blueprint(
    "clientes",
    __name__,
    url_prefix="/clientes"
)


@clientes_bp.route("/")
def listar():
    clientes = ClienteService.listar_clientes()

    return render_template(
        "clientes/lista.html",
        clientes=clientes
    )


@clientes_bp.route("/novo", methods=["GET", "POST"])
def novo():
    piscineiros = PiscineiroService.listar_ativos()

    if request.method == "POST":

        try:
            ClienteService.criar_cliente(
                nome=request.form.get("nome"),
                telefone=request.form.get("telefone"),
                whatsapp=request.form.get("whatsapp"),
                endereco=request.form.get("endereco"),
                cidade=request.form.get("cidade"),
                piscineiro_id=request.form.get("piscineiro_id") or None,
                observacao=request.form.get("observacao")
            )

            flash("Cliente cadastrado com sucesso.", "success")

            return redirect(url_for("clientes.listar"))

        except ValueError as erro:
            flash(str(erro), "error")

    return render_template(
        "clientes/novo.html",
        piscineiros=piscineiros
    )


@clientes_bp.route(
    "/<int:cliente_id>/editar",
    methods=["GET", "POST"]
)
def editar(cliente_id):
    cliente = ClienteService.buscar_por_id(cliente_id)

    if not cliente:
        return "Cliente não encontrado.", 404

    if request.method == "POST":

        try:
            ClienteService.editar_cliente(
                cliente_id=cliente_id,
                nome=request.form.get("nome"),
                telefone=request.form.get("telefone"),
                whatsapp=request.form.get("whatsapp"),
                endereco=request.form.get("endereco"),
                cidade=request.form.get("cidade"),
                observacao=request.form.get("observacao")
            )

            flash("Cliente atualizado com sucesso.", "success")

            return redirect(url_for("clientes.listar"))

        except ValueError as erro:
            flash(str(erro), "error")

    return render_template(
        "clientes/editar.html",
        cliente=cliente
    )


@clientes_bp.route(
    "/<int:cliente_id>/mudar-piscineiro",
    methods=["GET", "POST"]
)
def mudar_piscineiro(cliente_id):
    cliente = ClienteService.buscar_por_id(cliente_id)

    if not cliente:
        return "Cliente não encontrado.", 404

    piscineiros = PiscineiroService.listar_ativos()

    if request.method == "POST":

        try:
            ClienteService.mudar_piscineiro(
                cliente_id=cliente_id,
                novo_piscineiro_id=request.form.get("piscineiro_id") or None,
                observacao=request.form.get("observacao")
            )

            flash("Piscineiro do cliente atualizado com sucesso.", "success")

            return redirect(url_for("clientes.listar"))

        except ValueError as erro:
            flash(str(erro), "error")

    return render_template(
        "clientes/mudar_piscineiro.html",
        cliente=cliente,
        piscineiros=piscineiros
    )


@clientes_bp.route(
    "/<int:cliente_id>/status",
    methods=["POST"]
)
def alterar_status(cliente_id):

    try:
        ClienteService.alternar_status(cliente_id)

        flash("Status do cliente atualizado.", "success")

    except ValueError as erro:
        flash(str(erro), "error")

    return redirect(url_for("clientes.listar"))