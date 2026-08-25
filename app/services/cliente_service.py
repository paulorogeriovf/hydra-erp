# Hydra ERP
# Responsável por: concentrar as regras de negócio relacionadas aos clientes
# e controlar as mudanças de piscineiro responsável.

from app.extensions import db
from app.models.cliente import Cliente
from app.models.piscineiro import Piscineiro
from app.models.historico_piscineiro_cliente import HistoricoPiscineiroCliente

from decimal import Decimal

from app.models.notinha import Notinha
from app.models.item_notinha import ItemNotinha
from app.models.historico_piscineiro_cliente import HistoricoPiscineiroCliente
from app.services.notinha_service import NotinhaService


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

    @staticmethod
    def resumo_financeiro(cliente_id):

        cliente = ClienteService.buscar_por_id(
            cliente_id
        )

        if not cliente:
            raise ValueError(
                "Cliente não encontrado."
            )

        notinhas = (
            Notinha.query
            .filter(
                Notinha.cliente_id == cliente.id,
                Notinha.status != "CANCELADA"
            )
            .order_by(
                Notinha.data_retirada.desc()
            )
            .all()
        )

        total_comprado = Decimal("0.00")
        total_pago = Decimal("0.00")
        total_pendente = Decimal("0.00")
        total_vencido = Decimal("0.00")

        quantidade_notinhas = 0
        quantidade_vencidas = 0

        dados_notinhas = []

        for notinha in notinhas:

            quantidade_notinhas += 1

            valor = Decimal(
                str(notinha.valor_total)
            )

            pago = (
                NotinhaService.total_pago(
                    notinha
                )
            )

            saldo = (
                NotinhaService.saldo_pendente(
                    notinha
                )
            )

            situacao = (
                NotinhaService.situacao(
                    notinha
                )
            )

            total_comprado += valor
            total_pago += pago
            total_pendente += saldo

            if "VENCIDA" in situacao:
                quantidade_vencidas += 1
                total_vencido += saldo

            dados_notinhas.append({
                "notinha": notinha,
                "pago": pago,
                "saldo": saldo,
                "situacao": situacao
            })

        return {
            "total_comprado": total_comprado,
            "total_pago": total_pago,
            "total_pendente": total_pendente,
            "total_vencido": total_vencido,
            "quantidade_notinhas": quantidade_notinhas,
            "quantidade_vencidas": quantidade_vencidas,
            "notinhas": dados_notinhas
        }


    @staticmethod
    def historico_piscineiros(cliente_id):

        return (
            HistoricoPiscineiroCliente.query
            .filter_by(
                cliente_id=cliente_id
            )
            .order_by(
                HistoricoPiscineiroCliente.data_alteracao.desc()
            )
            .all()
        )


    @staticmethod
    def produtos_mais_comprados(cliente_id):

        resultados = (
            db.session.query(
                ItemNotinha.nome_produto,
                db.func.sum(
                    ItemNotinha.quantidade
                ).label("quantidade_total"),
                db.func.sum(
                    ItemNotinha.subtotal
                ).label("valor_total")
            )
            .join(
                Notinha,
                ItemNotinha.notinha_id == Notinha.id
            )
            .filter(
                Notinha.cliente_id == cliente_id,
                Notinha.status != "CANCELADA"
            )
            .group_by(
                ItemNotinha.nome_produto
            )
            .order_by(
                db.func.sum(
                    ItemNotinha.quantidade
                ).desc()
            )
            .limit(10)
            .all()
        )

        return resultados