# Hydra ERP
# Responsável por: concentrar as regras de negócio relacionadas
# aos produtos e registrar alterações importantes no histórico.

from decimal import Decimal, InvalidOperation

from app.extensions import db
from app.models.produto import Produto

from app.services.movimentacao_service import MovimentacaoService


class ProdutoService:

    # =========================================================
    # LISTAR
    # =========================================================

    @staticmethod
    def listar_produtos():

        return (
            Produto.query
            .order_by(
                Produto.nome.asc()
            )
            .all()
        )


    # =========================================================
    # BUSCAR
    # =========================================================

    @staticmethod
    def buscar_por_id(produto_id):

        return db.session.get(
            Produto,
            produto_id
        )


    # =========================================================
    # CONVERSÃO DECIMAL
    # =========================================================

    @staticmethod
    def _converter_decimal(
        valor,
        campo,
        obrigatorio=False
    ):

        if (
            valor is None
            or str(valor).strip() == ""
        ):

            if obrigatorio:

                raise ValueError(
                    f"{campo} é obrigatório."
                )

            return None


        try:

            numero = Decimal(
                str(valor).replace(",", ".")
            )


            if numero < 0:

                raise ValueError(
                    f"{campo} não pode ser negativo."
                )


            return numero


        except (
            InvalidOperation,
            TypeError,
            ValueError
        ):

            raise ValueError(
                f"{campo} possui um valor inválido."
            )


    # =========================================================
    # VALIDAR DADOS
    # =========================================================

    @staticmethod
    def validar_dados(
        nome,
        preco_normal,
        preco_atacado=None,
        gera_comissao=False,
        percentual_comissao=None
    ):

        nome = (
            nome or ""
        ).strip()


        if not nome:

            raise ValueError(
                "O nome do produto é obrigatório."
            )


        preco_normal = (
            ProdutoService._converter_decimal(
                preco_normal,
                "Preço normal",
                obrigatorio=True
            )
        )


        preco_atacado = (
            ProdutoService._converter_decimal(
                preco_atacado,
                "Preço atacado"
            )
        )


        if gera_comissao:

            percentual_comissao = (
                ProdutoService._converter_decimal(
                    percentual_comissao,
                    "Percentual de comissão",
                    obrigatorio=True
                )
            )


            if percentual_comissao > 100:

                raise ValueError(
                    "O percentual de comissão "
                    "não pode ser maior que 100%."
                )


        else:

            percentual_comissao = None


        return {

            "nome":
                nome,

            "preco_normal":
                preco_normal,

            "preco_atacado":
                preco_atacado,

            "percentual_comissao":
                percentual_comissao
        }


    # =========================================================
    # CRIAR PRODUTO
    # =========================================================

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

        dados = (
            ProdutoService.validar_dados(
                nome,
                preco_normal,
                preco_atacado,
                gera_comissao,
                percentual_comissao
            )
        )


        produto = Produto(

            nome=
                dados["nome"],

            marca=(
                marca or ""
            ).strip() or None,

            categoria=(
                categoria or ""
            ).strip() or None,

            preco_normal=
                dados["preco_normal"],

            preco_atacado=
                dados["preco_atacado"],

            gera_comissao=
                bool(gera_comissao),

            percentual_comissao=
                dados["percentual_comissao"],

            observacao=(
                observacao or ""
            ).strip() or None
        )


        try:

            db.session.add(
                produto
            )


            db.session.commit()


            # =================================================
            # AUDITORIA
            # =================================================

            descricao = (
                f"Produto {produto.nome} cadastrado. "
                f"Preço normal: "
                f"R$ {produto.preco_normal:.2f}."
            )


            if (
                produto.preco_atacado
                is not None
            ):

                descricao += (
                    f" Preço atacado: "
                    f"R$ {produto.preco_atacado:.2f}."
                )


            if produto.gera_comissao:

                descricao += (
                    f" Comissão: "
                    f"{produto.percentual_comissao}%."
                )


            MovimentacaoService.registrar(

                tipo=
                    "PRODUTO",

                acao=
                    "CRIAR",

                descricao=
                    descricao,

                entidade=
                    "PRODUTO",

                entidade_id=
                    produto.id
            )


            return produto


        except Exception:

            db.session.rollback()

            raise


    # =========================================================
    # EDITAR PRODUTO
    # =========================================================

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

        produto = (
            ProdutoService.buscar_por_id(
                produto_id
            )
        )


        if not produto:

            raise ValueError(
                "Produto não encontrado."
            )


        dados = (
            ProdutoService.validar_dados(
                nome,
                preco_normal,
                preco_atacado,
                gera_comissao,
                percentual_comissao
            )
        )


        # =====================================================
        # SNAPSHOT ANTERIOR
        # =====================================================

        nome_anterior = (
            produto.nome
        )

        marca_anterior = (
            produto.marca
        )

        categoria_anterior = (
            produto.categoria
        )

        preco_normal_anterior = (
            produto.preco_normal
        )

        preco_atacado_anterior = (
            produto.preco_atacado
        )

        gera_comissao_anterior = (
            produto.gera_comissao
        )

        percentual_anterior = (
            produto.percentual_comissao
        )

        observacao_anterior = (
            produto.observacao
        )


        # =====================================================
        # NOVOS VALORES
        # =====================================================

        produto.nome = (
            dados["nome"]
        )


        produto.marca = (
            marca or ""
        ).strip() or None


        produto.categoria = (
            categoria or ""
        ).strip() or None


        produto.preco_normal = (
            dados["preco_normal"]
        )


        produto.preco_atacado = (
            dados["preco_atacado"]
        )


        produto.gera_comissao = (
            bool(
                gera_comissao
            )
        )


        produto.percentual_comissao = (
            dados["percentual_comissao"]
        )


        produto.observacao = (
            observacao or ""
        ).strip() or None


        # =====================================================
        # DESCOBRIR ALTERAÇÕES
        # =====================================================

        alteracoes = []


        if (
            nome_anterior
            != produto.nome
        ):

            alteracoes.append(
                f"nome: "
                f"{nome_anterior} → "
                f"{produto.nome}"
            )


        if (
            marca_anterior
            != produto.marca
        ):

            alteracoes.append(
                "marca alterada"
            )


        if (
            categoria_anterior
            != produto.categoria
        ):

            alteracoes.append(
                "categoria alterada"
            )


        if (
            preco_normal_anterior
            != produto.preco_normal
        ):

            alteracoes.append(
                f"preço normal: "
                f"R$ {preco_normal_anterior:.2f} → "
                f"R$ {produto.preco_normal:.2f}"
            )


        if (
            preco_atacado_anterior
            != produto.preco_atacado
        ):

            valor_antigo = (
                f"R$ {preco_atacado_anterior:.2f}"
                if preco_atacado_anterior
                is not None
                else "Sem preço"
            )


            valor_novo = (
                f"R$ {produto.preco_atacado:.2f}"
                if produto.preco_atacado
                is not None
                else "Sem preço"
            )


            alteracoes.append(
                f"preço atacado: "
                f"{valor_antigo} → "
                f"{valor_novo}"
            )


        if (
            gera_comissao_anterior
            != produto.gera_comissao
        ):

            if produto.gera_comissao:

                alteracoes.append(
                    "comissão ativada"
                )

            else:

                alteracoes.append(
                    "comissão desativada"
                )


        if (
            percentual_anterior
            != produto.percentual_comissao
        ):

            percentual_antigo = (
                f"{percentual_anterior}%"
                if percentual_anterior
                is not None
                else "Sem comissão"
            )


            percentual_novo = (
                f"{produto.percentual_comissao}%"
                if produto.percentual_comissao
                is not None
                else "Sem comissão"
            )


            alteracoes.append(
                f"percentual de comissão: "
                f"{percentual_antigo} → "
                f"{percentual_novo}"
            )


        if (
            observacao_anterior
            != produto.observacao
        ):

            alteracoes.append(
                "observação alterada"
            )


        try:

            db.session.commit()


            # =================================================
            # AUDITORIA
            # =================================================

            if alteracoes:

                MovimentacaoService.registrar(

                    tipo=
                        "PRODUTO",

                    acao=
                        "EDITAR",

                    descricao=(
                        f"Produto "
                        f"{produto.nome} atualizado. "
                        f"Alterações: "
                        f"{'; '.join(alteracoes)}."
                    ),

                    entidade=
                        "PRODUTO",

                    entidade_id=
                        produto.id
                )


            return produto


        except Exception:

            db.session.rollback()

            raise


    # =========================================================
    # ALTERAR STATUS
    # =========================================================

    @staticmethod
    def alternar_status(produto_id):

        produto = (
            ProdutoService.buscar_por_id(
                produto_id
            )
        )


        if not produto:

            raise ValueError(
                "Produto não encontrado."
            )


        produto.ativo = (
            not produto.ativo
        )


        try:

            db.session.commit()


            status_texto = (
                "ativado"
                if produto.ativo
                else "inativado"
            )


            MovimentacaoService.registrar(

                tipo=
                    "PRODUTO",

                acao=
                    "STATUS",

                descricao=(
                    f"Produto "
                    f"{produto.nome} "
                    f"{status_texto}."
                ),

                entidade=
                    "PRODUTO",

                entidade_id=
                    produto.id
            )


            return produto


        except Exception:

            db.session.rollback()

            raise