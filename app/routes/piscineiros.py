# Hydra ERP
# Responsável por: disponibilizar as rotas de cadastro e gerenciamento de piscineiros.

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


@piscineiros_bp.route("/")
def listar():
    piscineiros = PiscineiroService.listar_piscineiros()

    return render_template(
        "piscineiros/lista.html",
        piscineiros=piscineiros
    )


@piscineiros_bp.route("/novo", methods=["GET", "POST"])
def novo():

    if request.method == "POST":

        try:
            PiscineiroService.criar_piscineiro(
                nome=request.form.get("nome"),
                telefone=request.form.get("telefone"),
                whatsapp=request.form.get("whatsapp"),
                cidade=request.form.get("cidade"),
                endereco=request.form.get("endereco"),
                observacao=request.form.get("observacao")
            )

            flash("Piscineiro cadastrado com sucesso.", "success")

            return redirect(url_for("piscineiros.listar"))

        except ValueError as erro:
            flash(str(erro), "error")

    return render_template("piscineiros/novo.html")


@piscineiros_bp.route(
    "/<int:piscineiro_id>/editar",
    methods=["GET", "POST"]
)
def editar(piscineiro_id):

    piscineiro = PiscineiroService.buscar_por_id(piscineiro_id)

    if not piscineiro:
        return "Piscineiro não encontrado.", 404

    if request.method == "POST":

        try:
            PiscineiroService.editar_piscineiro(
                piscineiro_id=piscineiro_id,
                nome=request.form.get("nome"),
                telefone=request.form.get("telefone"),
                whatsapp=request.form.get("whatsapp"),
                cidade=request.form.get("cidade"),
                endereco=request.form.get("endereco"),
                observacao=request.form.get("observacao")
            )

            flash("Piscineiro atualizado com sucesso.", "success")

            return redirect(url_for("piscineiros.listar"))

        except ValueError as erro:
            flash(str(erro), "error")

    return render_template(
        "piscineiros/editar.html",
        piscineiro=piscineiro
    )


@piscineiros_bp.route(
    "/<int:piscineiro_id>/status",
    methods=["POST"]
)
def alterar_status(piscineiro_id):

    try:
        PiscineiroService.alternar_status(piscineiro_id)

        flash("Status do piscineiro atualizado.", "success")

    except ValueError as erro:
        flash(str(erro), "error")

    return redirect(url_for("piscineiros.listar"))