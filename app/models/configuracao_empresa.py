# Hydra ERP
# Responsável por: armazenar os dados cadastrais
# e institucionais da empresa.

from app.extensions import db


class ConfiguracaoEmpresa(db.Model):

    __tablename__ = "configuracao_empresa"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    razao_social = db.Column(
        db.String(150),
        nullable=True
    )

    nome_fantasia = db.Column(
        db.String(150),
        nullable=True
    )

    cnpj = db.Column(
        db.String(30),
        nullable=True
    )

    inscricao_estadual = db.Column(
        db.String(50),
        nullable=True
    )

    inscricao_municipal = db.Column(
        db.String(50),
        nullable=True
    )

    telefone = db.Column(
        db.String(30),
        nullable=True
    )

    whatsapp = db.Column(
        db.String(30),
        nullable=True
    )

    email = db.Column(
        db.String(150),
        nullable=True
    )

    cep = db.Column(
        db.String(20),
        nullable=True
    )

    endereco = db.Column(
        db.String(200),
        nullable=True
    )

    numero = db.Column(
        db.String(20),
        nullable=True
    )

    complemento = db.Column(
        db.String(100),
        nullable=True
    )

    bairro = db.Column(
        db.String(100),
        nullable=True
    )

    cidade = db.Column(
        db.String(100),
        nullable=True
    )

    estado = db.Column(
        db.String(2),
        nullable=True
    )

    responsavel = db.Column(
        db.String(150),
        nullable=True
    )

    chave_pix = db.Column(
        db.String(150),
        nullable=True
    )

    banco = db.Column(
        db.String(100),
        nullable=True
    )

    agencia = db.Column(
        db.String(30),
        nullable=True
    )

    conta = db.Column(
        db.String(50),
        nullable=True
    )

    site = db.Column(
        db.String(200),
        nullable=True
    )

    observacao = db.Column(
        db.Text,
        nullable=True
    )