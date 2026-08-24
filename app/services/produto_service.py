# Hydra ERP
# Responsável por: concentrar as regras de negócio relacionadas aos produtos.

from decimal import Decimal, InvalidOperation

from app.extensions import db
from app.models.produto import Produto


class ProdutoService:

    @staticmethod
    def listar_produtos():
        return Produto.query.order_by(Produto.nome.asc()).all()

    @staticmethod
    def buscar_por_id(produto_id):
        return db.session.get(Produto, produto_id)

    @staticmethod
    def _converter_decimal(valor, campo, obrigatorio=False):
        if valor is None or str(valor).strip() == "":
            if obrigatorio:
                raise ValueError(f"{campo} é obrigatório.")
            return None

        try:
            numero = Decimal(str(valor).replace(",", "."))

            if numero < 0:
                raise ValueError(f"{campo} não pode ser negativo.")

            return numero

        except InvalidOperation:
            raise ValueError(f"{campo} possui um valor inválido.")

    @staticmethod
    def validar_dados(
        nome,
        preco_normal,
        preco_atacado=None,
        gera_comissao=False,
        percentual_comissao=None
    ):
        nome = (nome or "").strip()

        if not nome:
            raise ValueError("O nome do produto é obrigatório.")

        preco_normal = ProdutoService._converter_decimal(
            preco_normal,
            "Preço normal",
            obrigatorio=True
        )

        preco_atacado = ProdutoService._converter_decimal(
            preco_atacado,
            "Preço atacado"
        )

        if gera_comissao:
            percentual_comissao = ProdutoService._converter_decimal(
                percentual_comissao,
                "Percentual de comissão",
                obrigatorio=True
            )

            if percentual_comissao > 100:
                raise ValueError(
                    "O percentual de comissão não pode ser maior que 100%."
                )
        else:
            percentual_comissao = None

        return {
            "nome": nome,
            "preco_normal": preco_normal,
            "preco_atacado": preco_atacado,
            "percentual_comissao": percentual_comissao
        }

    @staticmethod
    def criar_produto(
        nome,
        marca,
        categoria,
        preco_normal,
        preco_atacado=None,
        gera_comissao=False,
        percentual_comissao=None,
        observacao=None
    ):
        dados = ProdutoService.validar_dados(
            nome,
            preco_normal,
            preco_atacado,
            gera_comissao,
            percentual_comissao
        )

        produto = Produto(
            nome=dados["nome"],
            marca=(marca or "").strip() or None,
            categoria=(categoria or "").strip() or None,
            preco_normal=dados["preco_normal"],
            preco_atacado=dados["preco_atacado"],
            gera_comissao=gera_comissao,
            percentual_comissao=dados["percentual_comissao"],
            observacao=(observacao or "").strip() or None
        )

        db.session.add(produto)
        db.session.commit()

        return produto

    @staticmethod
    def editar_produto(
        produto_id,
        nome,
        marca,
        categoria,
        preco_normal,
        preco_atacado=None,
        gera_comissao=False,
        percentual_comissao=None,
        observacao=None
    ):
        produto = ProdutoService.buscar_por_id(produto_id)

        if not produto:
            raise ValueError("Produto não encontrado.")

        dados = ProdutoService.validar_dados(
            nome,
            preco_normal,
            preco_atacado,
            gera_comissao,
            percentual_comissao
        )

        produto.nome = dados["nome"]
        produto.marca = (marca or "").strip() or None
        produto.categoria = (categoria or "").strip() or None
        produto.preco_normal = dados["preco_normal"]
        produto.preco_atacado = dados["preco_atacado"]
        produto.gera_comissao = gera_comissao
        produto.percentual_comissao = dados["percentual_comissao"]
        produto.observacao = (observacao or "").strip() or None

        db.session.commit()

        return produto

    @staticmethod
    def alternar_status(produto_id):
        produto = ProdutoService.buscar_por_id(produto_id)

        if not produto:
            raise ValueError("Produto não encontrado.")

        produto.ativo = not produto.ativo

        db.session.commit()

        return produto