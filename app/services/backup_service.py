# Hydra ERP
# Responsável por: gerar backups do banco MySQL
# e dos arquivos enviados ao sistema.

import os
import shutil
import subprocess
import tempfile
import zipfile

from datetime import datetime

from flask import current_app
from sqlalchemy.engine import make_url


class BackupService:

    @staticmethod
    def gerar_backup():

        agora = datetime.now()

        nome_base = agora.strftime(
            "hydra_backup_%Y-%m-%d_%H-%M-%S"
        )

        # Pasta raiz do projeto:
        # hydra-erp/
        pasta_projeto = os.path.abspath(
            os.path.join(
                current_app.root_path,
                ".."
            )
        )

        # Pasta onde os backups serão salvos
        pasta_backups = os.path.join(
            pasta_projeto,
            "backups"
        )

        os.makedirs(
            pasta_backups,
            exist_ok=True
        )

        arquivo_zip = os.path.join(
            pasta_backups,
            f"{nome_base}.zip"
        )

        # Pasta temporária usada durante a criação
        # do backup
        with tempfile.TemporaryDirectory() as pasta_temp:

            pasta_banco = os.path.join(
                pasta_temp,
                "banco"
            )

            os.makedirs(
                pasta_banco,
                exist_ok=True
            )

            arquivo_sql = os.path.join(
                pasta_banco,
                "hydra_erp.sql"
            )

            # 1. Exporta o banco MySQL
            BackupService._exportar_mysql(
                arquivo_sql
            )

            # 2. Copia os uploads
            BackupService._copiar_uploads(
                pasta_temp
            )

            # 3. Cria o ZIP final
            BackupService._criar_zip(
                pasta_temp,
                arquivo_zip
            )

        return arquivo_zip


    @staticmethod
    def _exportar_mysql(
        arquivo_destino
    ):

        db_uri = current_app.config.get(
            "SQLALCHEMY_DATABASE_URI"
        )

        if not db_uri:

            raise RuntimeError(
                "SQLALCHEMY_DATABASE_URI não configurada."
            )

        url = make_url(
            db_uri
        )

        host = url.host or "localhost"
        porta = url.port or 3306
        usuario = url.username
        senha = url.password or ""
        banco = url.database

        if not usuario or not banco:

            raise RuntimeError(
                "Não foi possível identificar "
                "o usuário ou o banco MySQL."
            )

        mysqldump = current_app.config.get(
            "MYSQLDUMP_PATH",
            "mysqldump"
        )

        comando = [
            mysqldump,

            "--host",
            host,

            "--port",
            str(porta),

            "--user",
            usuario,

            "--single-transaction",

            "--routines",

            "--triggers",

            "--default-character-set=utf8mb4",

            banco
        ]

        ambiente = os.environ.copy()

        if senha:

            ambiente["MYSQL_PWD"] = senha

        try:

            with open(
                arquivo_destino,
                "wb"
            ) as arquivo:

                resultado = subprocess.run(
                    comando,
                    stdout=arquivo,
                    stderr=subprocess.PIPE,
                    env=ambiente,
                    check=False
                )

        except FileNotFoundError:

            raise RuntimeError(
                "mysqldump não foi encontrado. "
                "Configure MYSQLDUMP_PATH "
                "com o caminho correto."
            )

        if resultado.returncode != 0:

            erro = resultado.stderr.decode(
                "utf-8",
                errors="ignore"
            )

            raise RuntimeError(
                f"Erro ao gerar backup do MySQL: {erro}"
            )


    @staticmethod
    def _copiar_uploads(
        pasta_temp
    ):

        pasta_uploads = current_app.config.get(
            "UPLOAD_FOLDER"
        )

        if not pasta_uploads:
            return

        if not os.path.exists(
            pasta_uploads
        ):
            return

        destino = os.path.join(
            pasta_temp,
            "uploads"
        )

        shutil.copytree(
            pasta_uploads,
            destino
        )


    @staticmethod
    def _criar_zip(
        pasta_origem,
        arquivo_zip
    ):

        with zipfile.ZipFile(
            arquivo_zip,
            "w",
            zipfile.ZIP_DEFLATED
        ) as zipf:

            for raiz, _, arquivos in os.walk(
                pasta_origem
            ):

                for arquivo in arquivos:

                    caminho_completo = os.path.join(
                        raiz,
                        arquivo
                    )

                    caminho_relativo = os.path.relpath(
                        caminho_completo,
                        pasta_origem
                    )

                    zipf.write(
                        caminho_completo,
                        caminho_relativo
                    )