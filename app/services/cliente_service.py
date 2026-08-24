# Hydra ERP
# Responsável por: concentrar as regras de negócio relacionadas aos clientes
# e controlar as mudanças de piscineiro responsável.

from app.extensions import db
from app.models.cliente import Cliente
from app.models.piscineiro import Piscineiro
from app.models.historico_piscineiro_cliente import HistoricoPiscineiroCliente


class ClienteService:

    @staticmethod
    def listar_clientes():
        return Cliente.query.order_by(Cliente.nome.asc()).all()

    @staticmethod
    def buscar_por_id(cliente_id):
        return db.session.get(Cliente, cliente_id)

    @staticmethod
    def criar_cliente(
        nome,
        telefone=None,
        whatsapp=None,
        endereco=None,
        cidade=None,
        piscineiro_id=None,
        observacao=None
    ):
        nome = (nome or "").strip()

        if not nome:
            raise ValueError("O nome do cliente é obrigatório.")

        piscineiro = None

        if piscineiro_id:
            piscineiro = db.session.get(Piscineiro, int(piscineiro_id))

            if not piscineiro:
                raise ValueError("Piscineiro selecionado não existe.")

            if not piscineiro.ativo:
                raise ValueError("Não é possível vincular um cliente a um piscineiro inativo.")

        cliente = Cliente(
            nome=nome,
            telefone=(telefone or "").strip() or None,
            whatsapp=(whatsapp or "").strip() or None,
            endereco=(endereco or "").strip() or None,
            cidade=(cidade or "").strip() or None,
            piscineiro_id=piscineiro.id if piscineiro else None,
            observacao=(observacao or "").strip() or None
        )

        db.session.add(cliente)
        db.session.flush()

        if piscineiro:
            historico = HistoricoPiscineiroCliente(
                cliente_id=cliente.id,
                piscineiro_anterior_id=None,
                piscineiro_novo_id=piscineiro.id,
                observacao="Vínculo inicial do cliente."
            )

            db.session.add(historico)

        db.session.commit()

        return cliente

    @staticmethod
    def editar_cliente(
        cliente_id,
        nome,
        telefone=None,
        whatsapp=None,
        endereco=None,
        cidade=None,
        observacao=None
    ):
        cliente = ClienteService.buscar_por_id(cliente_id)

        if not cliente:
            raise ValueError("Cliente não encontrado.")

        nome = (nome or "").strip()

        if not nome:
            raise ValueError("O nome do cliente é obrigatório.")

        cliente.nome = nome
        cliente.telefone = (telefone or "").strip() or None
        cliente.whatsapp = (whatsapp or "").strip() or None
        cliente.endereco = (endereco or "").strip() or None
        cliente.cidade = (cidade or "").strip() or None
        cliente.observacao = (observacao or "").strip() or None

        db.session.commit()

        return cliente

    @staticmethod
    def mudar_piscineiro(cliente_id, novo_piscineiro_id=None, observacao=None):
        cliente = ClienteService.buscar_por_id(cliente_id)

        if not cliente:
            raise ValueError("Cliente não encontrado.")

        piscineiro_anterior_id = cliente.piscineiro_id

        novo_piscineiro = None

        if novo_piscineiro_id:
            novo_piscineiro = db.session.get(
                Piscineiro,
                int(novo_piscineiro_id)
            )

            if not novo_piscineiro:
                raise ValueError("Piscineiro selecionado não existe.")

            if not novo_piscineiro.ativo:
                raise ValueError(
                    "Não é possível vincular o cliente a um piscineiro inativo."
                )

        novo_id = novo_piscineiro.id if novo_piscineiro else None

        if piscineiro_anterior_id == novo_id:
            raise ValueError(
                "O cliente já está vinculado a esse piscineiro."
            )

        cliente.piscineiro_id = novo_id

        historico = HistoricoPiscineiroCliente(
            cliente_id=cliente.id,
            piscineiro_anterior_id=piscineiro_anterior_id,
            piscineiro_novo_id=novo_id,
            observacao=(observacao or "").strip() or None
        )

        db.session.add(historico)
        db.session.commit()

        return cliente

    @staticmethod
    def alternar_status(cliente_id):
        cliente = ClienteService.buscar_por_id(cliente_id)

        if not cliente:
            raise ValueError("Cliente não encontrado.")

        cliente.ativo = not cliente.ativo

        db.session.commit()

        return cliente