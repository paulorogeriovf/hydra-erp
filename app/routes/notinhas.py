# Hydra ERP
# Responsável por: disponibilizar as rotas de criação,
# consulta, organização, pagamentos, observações
# e anexos das notinhas.

from datetime import date, timedelta

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
    current_app
)

from app.services.notinha_service import NotinhaService
from app.services.pagamento_service import PagamentoService
from app.services.cliente_service import ClienteService
from app.services.produto_service import ProdutoService
from app.services.observacao_notinha_service import ObservacaoNotinhaService
from app.services.anexo_notinha_service import AnexoNotinhaService


notinhas_bp = Blueprint(
    "notinhas",
    __name__,
    url_prefix="/notinhas"
)


# =========================================================
# PÁGINA PRINCIPAL / PASTAS
# =========================================================

@notinhas_bp.route("/")
def listar():

    busca = (
        request.args.get(
            "busca",
            ""
        )
        .strip()
    )

    todas_notinhas = (
        NotinhaService.listar_notinhas()
    )

    pastas = {}

    quantidade_diretas = 0


    # =====================================================
    # ORGANIZAR PASTAS POR PISCINEIRO
    # =====================================================

    for notinha in todas_notinhas:

        if notinha.piscineiro:

            piscineiro_id = (
                notinha.piscineiro.id
            )

            if piscineiro_id not in pastas:

                pastas[piscineiro_id] = {
                    "piscineiro":
                        notinha.piscineiro,

                    "quantidade_notinhas":
                        0,

                    "clientes":
                        set()
                }


            pastas[
                piscineiro_id
            ][
                "quantidade_notinhas"
            ] += 1


            pastas[
                piscineiro_id
            ][
                "clientes"
            ].add(
                notinha.cliente_id
            )

        else:

            quantidade_diretas += 1


    # =====================================================
    # BUSCA GERAL
    # =====================================================

    resultados_busca = []

    if busca:

        busca_lower = (
            busca.lower()
        )


        for notinha in todas_notinhas:

            cliente_nome = (
                notinha.cliente.nome.lower()
                if notinha.cliente
                else ""
            )

            piscineiro_nome = (
                notinha.piscineiro.nome.lower()
                if notinha.piscineiro
                else ""
            )

            id_notinha = (
                str(notinha.id)
            )


            if (
                busca_lower in cliente_nome
                or busca_lower in piscineiro_nome
                or busca_lower in id_notinha
            ):

                resultados_busca.append({

                    "notinha":
                        notinha,

                    "saldo":
                        NotinhaService.saldo_pendente(
                            notinha
                        ),

                    "situacao":
                        NotinhaService.situacao(
                            notinha
                        )
                })


    return render_template(
        "notinhas/lista.html",

        pastas=list(
            pastas.values()
        ),

        quantidade_diretas=
            quantidade_diretas,

        busca=
            busca,

        resultados_busca=
            resultados_busca
    )


# =========================================================
# NOVA NOTINHA
# =========================================================

@notinhas_bp.route(
    "/nova",
    methods=["GET", "POST"]
)
def nova():

    clientes = [
        cliente
        for cliente
        in ClienteService.listar_clientes()

        if cliente.ativo
    ]


    produtos = [
        produto
        for produto
        in ProdutoService.listar_produtos()

        if produto.ativo
    ]


    if request.method == "POST":

        try:

            # =================================================
            # ITENS
            # =================================================

            produto_ids = (
                request.form.getlist(
                    "produto_id[]"
                )
            )

            quantidades = (
                request.form.getlist(
                    "quantidade[]"
                )
            )

            precos = (
                request.form.getlist(
                    "preco_unitario[]"
                )
            )


            itens = []


            for (
                produto_id,
                quantidade,
                preco
            ) in zip(
                produto_ids,
                quantidades,
                precos
            ):

                if not produto_id:
                    continue


                itens.append({
                    "produto_id":
                        produto_id,

                    "quantidade":
                        quantidade,

                    "preco_unitario":
                        preco
                })


            # =================================================
            # CRIAR NOTINHA
            # =================================================

            notinha = (
                NotinhaService.criar_notinha(

                    cliente_id=
                        request.form.get(
                            "cliente_id"
                        ),

                    data_retirada=
                        date.fromisoformat(
                            request.form.get(
                                "data_retirada"
                            )
                        ),

                    data_vencimento=
                        date.fromisoformat(
                            request.form.get(
                                "data_vencimento"
                            )
                        ),

                    itens=
                        itens,

                    responsavel_cobranca=
                        request.form.get(
                            "responsavel_cobranca"
                        ),

                    observacao=
                        request.form.get(
                            "observacao"
                        )
                )
            )


            # =================================================
            # FOTO / ANEXO ORIGINAL
            # =================================================

            arquivo = (
                request.files.get(
                    "arquivo"
                )
            )


            if (
                arquivo
                and arquivo.filename
            ):

                AnexoNotinhaService.salvar(

                    notinha_id=
                        notinha.id,

                    arquivo=
                        arquivo,

                    tipo=
                        "ORIGINAL",

                    observacao=
                        "Arquivo anexado durante o cadastro da notinha."
                )


            flash(
                "Notinha cadastrada com sucesso.",
                "success"
            )


            return redirect(
                url_for(
                    "notinhas.detalhes",
                    notinha_id=notinha.id
                )
            )


        except (
            ValueError,
            TypeError
        ) as erro:

            flash(
                str(erro),
                "error"
            )


    return render_template(
        "notinhas/nova.html",

        clientes=
            clientes,

        produtos=
            produtos,

        hoje=
            date.today().isoformat(),

        vencimento_padrao=(
            date.today()
            + timedelta(days=30)
        ).isoformat()
    )


# =========================================================
# PASTA DO PISCINEIRO
# =========================================================

@notinhas_bp.route(
    "/piscineiro/<int:piscineiro_id>"
)
def pasta_piscineiro(piscineiro_id):

    modo = (
        request.args.get(
            "status",
            "pendentes"
        )
        .strip()
        .lower()
    )

    todas_notinhas = [

        notinha

        for notinha
        in NotinhaService.listar_notinhas()

        if (
            notinha.piscineiro_id
            == piscineiro_id
        )
    ]


    if not todas_notinhas:

        return (
            "Nenhuma notinha encontrada "
            "para este piscineiro.",
            404
        )


    piscineiro = (
        todas_notinhas[0].piscineiro
    )


    # =====================================================
    # RESUMO
    # =====================================================

    quantidade_pendentes = 0
    quantidade_vencidas = 0
    quantidade_pagas = 0


    for notinha in todas_notinhas:

        situacao = (
            NotinhaService.situacao(
                notinha
            )
        )


        if situacao == "PAGA":

            quantidade_pagas += 1

        elif situacao != "CANCELADA":

            quantidade_pendentes += 1


            if "VENCIDA" in situacao:

                quantidade_vencidas += 1


    # =====================================================
    # FILTRAR
    # =====================================================

    notinhas_filtradas = []


    for notinha in todas_notinhas:

        situacao = (
            NotinhaService.situacao(
                notinha
            )
        )


        if modo == "pagas":

            if situacao != "PAGA":
                continue

        else:

            if situacao in {
                "PAGA",
                "CANCELADA"
            }:
                continue


        notinhas_filtradas.append(
            notinha
        )


    # =====================================================
    # AGRUPAR POR CLIENTE
    # =====================================================

    clientes = {}


    for notinha in notinhas_filtradas:

        cliente_id = (
            notinha.cliente.id
        )


        if cliente_id not in clientes:

            clientes[
                cliente_id
            ] = {

                "cliente":
                    notinha.cliente,

                "notinhas":
                    []
            }


        clientes[
            cliente_id
        ][
            "notinhas"
        ].append({

            "notinha":
                notinha,

            "saldo":
                NotinhaService.saldo_pendente(
                    notinha
                ),

            "situacao":
                NotinhaService.situacao(
                    notinha
                )
        })


    return render_template(
        "notinhas/pasta_piscineiro.html",

        piscineiro=
            piscineiro,

        clientes=list(
            clientes.values()
        ),

        modo=
            modo,

        quantidade_pendentes=
            quantidade_pendentes,

        quantidade_vencidas=
            quantidade_vencidas,

        quantidade_pagas=
            quantidade_pagas
    )


# =========================================================
# PASTA HYDRA / DIRETO
# =========================================================

@notinhas_bp.route(
    "/diretas"
)
def pasta_diretas():

    modo = (
        request.args.get(
            "status",
            "pendentes"
        )
        .strip()
        .lower()
    )


    todas_notinhas = [

        notinha

        for notinha
        in NotinhaService.listar_notinhas()

        if (
            notinha.piscineiro_id
            is None
        )
    ]


    # =====================================================
    # RESUMO
    # =====================================================

    quantidade_pendentes = 0
    quantidade_vencidas = 0
    quantidade_pagas = 0


    for notinha in todas_notinhas:

        situacao = (
            NotinhaService.situacao(
                notinha
            )
        )


        if situacao == "PAGA":

            quantidade_pagas += 1

        elif situacao != "CANCELADA":

            quantidade_pendentes += 1


            if "VENCIDA" in situacao:

                quantidade_vencidas += 1


    # =====================================================
    # FILTRAR
    # =====================================================

    notinhas_filtradas = []


    for notinha in todas_notinhas:

        situacao = (
            NotinhaService.situacao(
                notinha
            )
        )


        if modo == "pagas":

            if situacao != "PAGA":
                continue

        else:

            if situacao in {
                "PAGA",
                "CANCELADA"
            }:
                continue


        notinhas_filtradas.append(
            notinha
        )


    # =====================================================
    # AGRUPAR POR CLIENTE
    # =====================================================

    clientes = {}


    for notinha in notinhas_filtradas:

        cliente_id = (
            notinha.cliente.id
        )


        if cliente_id not in clientes:

            clientes[
                cliente_id
            ] = {

                "cliente":
                    notinha.cliente,

                "notinhas":
                    []
            }


        clientes[
            cliente_id
        ][
            "notinhas"
        ].append({

            "notinha":
                notinha,

            "saldo":
                NotinhaService.saldo_pendente(
                    notinha
                ),

            "situacao":
                NotinhaService.situacao(
                    notinha
                )
        })


    return render_template(
        "notinhas/pasta_diretas.html",

        clientes=list(
            clientes.values()
        ),

        modo=
            modo,

        quantidade_pendentes=
            quantidade_pendentes,

        quantidade_vencidas=
            quantidade_vencidas,

        quantidade_pagas=
            quantidade_pagas
    )


# =========================================================
# DETALHES DA NOTINHA
# =========================================================

@notinhas_bp.route(
    "/<int:notinha_id>"
)
def detalhes(notinha_id):

    notinha = (
        NotinhaService.buscar_por_id(
            notinha_id
        )
    )


    if not notinha:

        return (
            "Notinha não encontrada.",
            404
        )


    return render_template(
        "notinhas/detalhes.html",

        notinha=
            notinha,

        total_pago=
            NotinhaService.total_pago(
                notinha
            ),

        saldo=
            NotinhaService.saldo_pendente(
                notinha
            ),

        situacao=
            NotinhaService.situacao(
                notinha
            ),

        hoje=
            date.today().isoformat()
    )


# =========================================================
# REGISTRAR PAGAMENTO
# =========================================================

@notinhas_bp.route(
    "/<int:notinha_id>/pagamento",
    methods=["POST"]
)
def registrar_pagamento(notinha_id):

    try:

        PagamentoService.registrar_pagamento(

            notinha_id=
                notinha_id,

            valor=
                request.form.get(
                    "valor"
                ),

            data_pagamento=
                date.fromisoformat(
                    request.form.get(
                        "data_pagamento"
                    )
                ),

            pago_por=
                request.form.get(
                    "pago_por"
                ),

            forma_pagamento=
                request.form.get(
                    "forma_pagamento"
                ),

            observacao=
                request.form.get(
                    "observacao"
                )
        )


        flash(
            "Pagamento registrado com sucesso.",
            "success"
        )


    except (
        ValueError,
        TypeError
    ) as erro:

        flash(
            str(erro),
            "error"
        )


    return redirect(
        url_for(
            "notinhas.detalhes",
            notinha_id=notinha_id
        )
    )


# =========================================================
# OBSERVAÇÕES
# =========================================================

@notinhas_bp.route(
    "/<int:notinha_id>/observacao",
    methods=["POST"]
)
def adicionar_observacao(notinha_id):

    try:

        ObservacaoNotinhaService.adicionar(

            notinha_id=
                notinha_id,

            texto=
                request.form.get(
                    "texto"
                )
        )


        flash(
            "Observação adicionada com sucesso.",
            "success"
        )


    except (
        ValueError,
        TypeError
    ) as erro:

        flash(
            str(erro),
            "error"
        )


    return redirect(
        url_for(
            "notinhas.detalhes",
            notinha_id=notinha_id
        )
    )


# =========================================================
# ADICIONAR ANEXO
# =========================================================

@notinhas_bp.route(
    "/<int:notinha_id>/anexo",
    methods=["POST"]
)
def adicionar_anexo(notinha_id):

    try:

        arquivo = (
            request.files.get(
                "arquivo"
            )
        )


        AnexoNotinhaService.salvar(

            notinha_id=
                notinha_id,

            arquivo=
                arquivo,

            tipo=
                request.form.get(
                    "tipo"
                ),

            pagamento_id=
                request.form.get(
                    "pagamento_id"
                )
                or None,

            observacao=
                request.form.get(
                    "observacao"
                )
        )


        flash(
            "Arquivo anexado com sucesso.",
            "success"
        )


    except (
        ValueError,
        TypeError
    ) as erro:

        flash(
            str(erro),
            "error"
        )


    return redirect(
        url_for(
            "notinhas.detalhes",
            notinha_id=notinha_id
        )
    )


# =========================================================
# VISUALIZAR ANEXO
# =========================================================

@notinhas_bp.route(
    "/anexos/<path:caminho>"
)
def visualizar_anexo(caminho):

    return send_from_directory(

        current_app.config[
            "UPLOAD_FOLDER"
        ],

        caminho
    )