# Hydra ERP
# Responsável por: concentrar as regras de negócio relacionadas aos piscineiros.

from app.extensions import db
from app.models.piscineiro import Piscineiro


class PiscineiroService:

    @staticmethod
    def listar_piscineiros():
        return Piscineiro.query.order_by(Piscineiro.nome.asc()).all()

    @staticmethod
    def listar_ativos():
        return (
            Piscineiro.query
            .filter_by(ativo=True)
            .order_by(Piscineiro.nome.asc())
            .all()
        )

    @staticmethod
    def buscar_por_id(piscineiro_id):
        return db.session.get(Piscineiro, piscineiro_id)

    @staticmethod
    def criar_piscineiro(
        nome,
        telefone=None,
        whatsapp=None,
        cidade=None,
        endereco=None,
        observacao=None
    ):
        nome = (nome or "").strip()

        if not nome:
            raise ValueError("O nome do piscineiro é obrigatório.")

        piscineiro = Piscineiro(
            nome=nome,
            telefone=(telefone or "").strip() or None,
            whatsapp=(whatsapp or "").strip() or None,
            cidade=(cidade or "").strip() or None,
            endereco=(endereco or "").strip() or None,
            observacao=(observacao or "").strip() or None
        )

        db.session.add(piscineiro)
        db.session.commit()

        return piscineiro

    @staticmethod
    def editar_piscineiro(
        piscineiro_id,
        nome,
        telefone=None,
        whatsapp=None,
        cidade=None,
        endereco=None,
        observacao=None
    ):
        piscineiro = PiscineiroService.buscar_por_id(piscineiro_id)

        if not piscineiro:
            raise ValueError("Piscineiro não encontrado.")

        nome = (nome or "").strip()

        if not nome:
            raise ValueError("O nome do piscineiro é obrigatório.")

        piscineiro.nome = nome
        piscineiro.telefone = (telefone or "").strip() or None
        piscineiro.whatsapp = (whatsapp or "").strip() or None
        piscineiro.cidade = (cidade or "").strip() or None
        piscineiro.endereco = (endereco or "").strip() or None
        piscineiro.observacao = (observacao or "").strip() or None

        db.session.commit()

        return piscineiro

    @staticmethod
    def alternar_status(piscineiro_id):
        piscineiro = PiscineiroService.buscar_por_id(piscineiro_id)

        if not piscineiro:
            raise ValueError("Piscineiro não encontrado.")

        piscineiro.ativo = not piscineiro.ativo

        db.session.commit()

        return piscineiro