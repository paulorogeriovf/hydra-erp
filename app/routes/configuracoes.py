# Hydra ERP
# Responsável por: exibir e editar
# as configurações gerais da empresa.

import os

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file
)

from app.extensions import db
from app.models.configuracao_empresa import ConfiguracaoEmpresa
from app.services.backup_service import BackupService


configuracoes_bp = Blueprint(
    "configuracoes",
    __name__,
    url_prefix="/configuracoes"
)


def obter_empresa():

    empresa = ConfiguracaoEmpresa.query.first()

    if not empresa:

        empresa = ConfiguracaoEmpresa(
            nome_fantasia="Hydra Piscinas e Lazer"
        )

        db.session.add(empresa)
        db.session.commit()

    return empresa


@configuracoes_bp.route("/")
def index():

    empresa = obter_empresa()

    return render_template(
        "configuracoes/index.html",
        empresa=empresa
    )


@configuracoes_bp.route(
    "/editar",
    methods=["GET", "POST"]
)
def editar():

    empresa = obter_empresa()

    if request.method == "POST":

        empresa.razao_social = (
            request.form.get("razao_social") or None
        )

        empresa.nome_fantasia = (
            request.form.get("nome_fantasia") or None
        )

        empresa.cnpj = (
            request.form.get("cnpj") or None
        )

        empresa.inscricao_estadual = (
            request.form.get("inscricao_estadual") or None
        )

        empresa.inscricao_municipal = (
            request.form.get("inscricao_municipal") or None
        )

        empresa.telefone = (
            request.form.get("telefone") or None
        )

        empresa.whatsapp = (
            request.form.get("whatsapp") or None
        )

        empresa.email = (
            request.form.get("email") or None
        )

        empresa.cep = (
            request.form.get("cep") or None
        )

        empresa.endereco = (
            request.form.get("endereco") or None
        )

        empresa.numero = (
            request.form.get("numero") or None
        )

        empresa.complemento = (
            request.form.get("complemento") or None
        )

        empresa.bairro = (
            request.form.get("bairro") or None
        )

        empresa.cidade = (
            request.form.get("cidade") or None
        )

        empresa.estado = (
            request.form.get("estado") or None
        )

        empresa.responsavel = (
            request.form.get("responsavel") or None
        )

        empresa.chave_pix = (
            request.form.get("chave_pix") or None
        )

        empresa.banco = (
            request.form.get("banco") or None
        )

        empresa.agencia = (
            request.form.get("agencia") or None
        )

        empresa.conta = (
            request.form.get("conta") or None
        )

        empresa.site = (
            request.form.get("site") or None
        )

        empresa.observacao = (
            request.form.get("observacao") or None
        )

        db.session.commit()

        flash(
            "Dados da empresa atualizados com sucesso.",
            "success"
        )

        return redirect(
            url_for("configuracoes.index")
        )

    return render_template(
        "configuracoes/editar.html",
        empresa=empresa
    )

@configuracoes_bp.route(
    "/backup",
    methods=["POST"]
)
def gerar_backup():

    try:

        arquivo = BackupService.gerar_backup()

        flash(
            "Backup gerado com sucesso.",
            "success"
        )

        return send_file(
            arquivo,
            as_attachment=True,
            download_name=os.path.basename(
                arquivo
            )
        )

    except Exception as erro:

        flash(
            f"Não foi possível gerar o backup: {erro}",
            "error"
        )

        return redirect(
            url_for(
                "configuracoes.index"
            )
        )