# Hydra ERP
# Responsável por: salvar e registrar fotos, comprovantes
# e outros arquivos relacionados às notinhas.

import os
import uuid

from werkzeug.utils import secure_filename

from flask import current_app

from app.extensions import db
from app.models.notinha import Notinha
from app.models.pagamento import Pagamento
from app.models.anexo_notinha import AnexoNotinha


class AnexoNotinhaService:

    EXTENSOES_PERMITIDAS = {
        "jpg",
        "jpeg",
        "png",
        "pdf"
    }

    @staticmethod
    def extensao_permitida(nome_arquivo):

        return (
            "." in nome_arquivo
            and nome_arquivo
                .rsplit(".", 1)[1]
                .lower()
                in AnexoNotinhaService.EXTENSOES_PERMITIDAS
        )

    @staticmethod
    def salvar(
        notinha_id,
        arquivo,
        tipo="OUTRO",
        pagamento_id=None,
        observacao=None
    ):

        notinha = db.session.get(
            Notinha,
            int(notinha_id)
        )

        if not notinha:
            raise ValueError(
                "Notinha não encontrada."
            )

        if not arquivo:
            raise ValueError(
                "Nenhum arquivo foi enviado."
            )

        nome_original = (
            arquivo.filename or ""
        ).strip()

        if not nome_original:
            raise ValueError(
                "Arquivo inválido."
            )

        if not AnexoNotinhaService.extensao_permitida(
            nome_original
        ):
            raise ValueError(
                "Formato não permitido. Use JPG, JPEG, PNG ou PDF."
            )

        tipo = (
            tipo or "OUTRO"
        ).upper()

        tipos_permitidos = {
            "ORIGINAL",
            "ATUALIZACAO",
            "COMPROVANTE",
            "OUTRO"
        }

        if tipo not in tipos_permitidos:
            raise ValueError(
                "Tipo de anexo inválido."
            )

        pagamento = None

        if pagamento_id:

            pagamento = db.session.get(
                Pagamento,
                int(pagamento_id)
            )

            if not pagamento:
                raise ValueError(
                    "Pagamento relacionado não encontrado."
                )

            if pagamento.notinha_id != notinha.id:
                raise ValueError(
                    "O pagamento informado não pertence a esta notinha."
                )

        nome_seguro = secure_filename(
            nome_original
        )

        extensao = (
            nome_seguro
            .rsplit(".", 1)[1]
            .lower()
        )

        nome_arquivo = (
            f"{uuid.uuid4().hex}.{extensao}"
        )

        pasta_relativa = os.path.join(
            "notinhas",
            str(notinha.id)
        )

        pasta_absoluta = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            pasta_relativa
        )

        os.makedirs(
            pasta_absoluta,
            exist_ok=True
        )

        caminho_absoluto = os.path.join(
            pasta_absoluta,
            nome_arquivo
        )

        caminho_relativo = os.path.join(
            pasta_relativa,
            nome_arquivo
        ).replace("\\", "/")

        try:

            arquivo.save(
                caminho_absoluto
            )

            anexo = AnexoNotinha(
                notinha_id=notinha.id,

                pagamento_id=(
                    pagamento.id
                    if pagamento
                    else None
                ),

                tipo=tipo,

                nome_original=nome_original,

                nome_arquivo=nome_arquivo,

                caminho=caminho_relativo,

                observacao=(
                    observacao or ""
                ).strip() or None
            )

            db.session.add(
                anexo
            )

            db.session.commit()

            return anexo

        except Exception:

            db.session.rollback()

            if os.path.exists(
                caminho_absoluto
            ):
                os.remove(
                    caminho_absoluto
                )

            raise