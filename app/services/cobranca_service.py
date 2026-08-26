# Hydra ERP
# Responsável por: organizar cobranças vencidas
# e notinhas próximas do vencimento.

from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from app.models.notinha import Notinha
from app.services.notinha_service import NotinhaService


class CobrancaService:

    # =========================================================
    # CONFIGURAÇÃO TEMPORÁRIA
    # =========================================================
    # Futuramente esse valor será controlado
    # pelo módulo Configurações.

    DIAS_ALERTA_VENCIMENTO = 5


    # =========================================================
    # LISTAR VENCIDAS
    # =========================================================

    @staticmethod
    def listar_vencidas():

        notinhas = (
            Notinha.query
            .filter(
                Notinha.status.notin_(
                    [
                        "PAGA",
                        "CANCELADA"
                    ]
                )
            )
            .order_by(
                Notinha.data_vencimento.asc()
            )
            .all()
        )

        resultado = []


        for notinha in notinhas:

            saldo = (
                NotinhaService.saldo_pendente(
                    notinha
                )
            )


            # Sem saldo, não existe cobrança.
            if saldo <= 0:
                continue


            dias_atraso = (
                NotinhaService.dias_atraso(
                    notinha
                )
            )


            # Ainda não venceu.
            if dias_atraso <= 0:
                continue


            resultado.append({

                "notinha":
                    notinha,

                "saldo":
                    saldo,

                "total_pago":
                    NotinhaService.total_pago(
                        notinha
                    ),

                "situacao":
                    NotinhaService.situacao(
                        notinha
                    ),

                "dias_atraso":
                    dias_atraso,

                "mensagem_cobranca":
                    NotinhaService.mensagem_cobranca(
                        notinha
                    )
            })


        return resultado


    # =========================================================
    # LISTAR PRÓXIMAS DO VENCIMENTO
    # =========================================================

    @staticmethod
    def listar_proximas_vencimento():

        hoje = date.today()

        limite = (
            hoje
            + timedelta(
                days=CobrancaService.DIAS_ALERTA_VENCIMENTO
            )
        )


        notinhas = (
            Notinha.query
            .filter(
                Notinha.status.notin_(
                    [
                        "PAGA",
                        "CANCELADA"
                    ]
                ),

                Notinha.data_vencimento >= hoje,

                Notinha.data_vencimento <= limite
            )
            .order_by(
                Notinha.data_vencimento.asc()
            )
            .all()
        )


        resultado = []


        for notinha in notinhas:

            saldo = (
                NotinhaService.saldo_pendente(
                    notinha
                )
            )


            if saldo <= 0:
                continue


            dias_restantes = (
                notinha.data_vencimento
                - hoje
            ).days


            resultado.append({

                "notinha":
                    notinha,

                "saldo":
                    saldo,

                "total_pago":
                    NotinhaService.total_pago(
                        notinha
                    ),

                "situacao":
                    NotinhaService.situacao(
                        notinha
                    ),

                "dias_restantes":
                    dias_restantes,

                "mensagem_lembrete":
                    NotinhaService.mensagem_lembrete(
                        notinha
                    )
            })


        return resultado


    # =========================================================
    # RESUMO
    # =========================================================

    @staticmethod
    def resumo():

        vencidas = (
            CobrancaService.listar_vencidas()
        )

        proximas = (
            CobrancaService.listar_proximas_vencimento()
        )


        total_vencido = Decimal(
            "0.00"
        )

        total_proximo = Decimal(
            "0.00"
        )

        clientes_em_atraso = set()

        maior_atraso = 0


        # =====================================================
        # VENCIDAS
        # =====================================================

        for dados in vencidas:

            total_vencido += (
                dados["saldo"]
            )


            notinha = (
                dados["notinha"]
            )


            if notinha.cliente_id:

                clientes_em_atraso.add(
                    notinha.cliente_id
                )


            if (
                dados["dias_atraso"]
                > maior_atraso
            ):

                maior_atraso = (
                    dados["dias_atraso"]
                )


        # =====================================================
        # PRÓXIMAS
        # =====================================================

        for dados in proximas:

            total_proximo += (
                dados["saldo"]
            )


        return {

            "total_vencido":
                total_vencido,

            "quantidade_vencidas":
                len(vencidas),

            "clientes_em_atraso":
                len(clientes_em_atraso),

            "maior_atraso":
                maior_atraso,

            "total_proximo":
                total_proximo,

            "quantidade_proximas":
                len(proximas),

            "dias_alerta":
                CobrancaService.DIAS_ALERTA_VENCIMENTO
        }


    # =========================================================
    # AGRUPAR VENCIDAS POR RESPONSÁVEL
    # =========================================================

    @staticmethod
    def agrupar_por_responsavel():

        vencidas = (
            CobrancaService.listar_vencidas()
        )


        hydra = defaultdict(
            list
        )


        piscineiros = defaultdict(
            lambda: {

                "piscineiro":
                    None,

                "clientes":
                    defaultdict(
                        list
                    )
            }
        )


        for dados in vencidas:

            notinha = (
                dados["notinha"]
            )


            cliente = (
                notinha.cliente
            )


            # =================================================
            # HYDRA É RESPONSÁVEL
            # =================================================

            if (
                notinha.responsavel_cobranca
                == "HYDRA"
            ):

                hydra[
                    cliente.id
                ].append(
                    dados
                )

                continue


            # =================================================
            # PISCINEIRO É RESPONSÁVEL
            # =================================================

            if (
                notinha.responsavel_cobranca
                == "PISCINEIRO"
                and notinha.piscineiro
            ):

                piscineiro_id = (
                    notinha.piscineiro.id
                )


                piscineiros[
                    piscineiro_id
                ][
                    "piscineiro"
                ] = (
                    notinha.piscineiro
                )


                piscineiros[
                    piscineiro_id
                ][
                    "clientes"
                ][
                    cliente.id
                ].append(
                    dados
                )


            else:

                # Segurança:
                # se não houver piscineiro,
                # a cobrança fica com a Hydra.

                hydra[
                    cliente.id
                ].append(
                    dados
                )


        return {

            "hydra":
                hydra,

            "piscineiros":
                piscineiros
        }


    # =========================================================
    # AGRUPAR PRÓXIMAS DO VENCIMENTO
    # =========================================================

    @staticmethod
    def agrupar_proximas():

        proximas = (
            CobrancaService.listar_proximas_vencimento()
        )


        hydra = defaultdict(
            list
        )


        piscineiros = defaultdict(
            lambda: {

                "piscineiro":
                    None,

                "clientes":
                    defaultdict(
                        list
                    )
            }
        )


        for dados in proximas:

            notinha = (
                dados["notinha"]
            )


            cliente = (
                notinha.cliente
            )


            # =================================================
            # HYDRA É RESPONSÁVEL
            # =================================================

            if (
                notinha.responsavel_cobranca
                == "HYDRA"
            ):

                hydra[
                    cliente.id
                ].append(
                    dados
                )

                continue


            # =================================================
            # PISCINEIRO É RESPONSÁVEL
            # =================================================

            if (
                notinha.responsavel_cobranca
                == "PISCINEIRO"
                and notinha.piscineiro
            ):

                piscineiro_id = (
                    notinha.piscineiro.id
                )


                piscineiros[
                    piscineiro_id
                ][
                    "piscineiro"
                ] = (
                    notinha.piscineiro
                )


                piscineiros[
                    piscineiro_id
                ][
                    "clientes"
                ][
                    cliente.id
                ].append(
                    dados
                )


            else:

                hydra[
                    cliente.id
                ].append(
                    dados
                )


        return {

            "hydra":
                hydra,

            "piscineiros":
                piscineiros
        }

        # =====================================================
    # MENSAGEM DE LEMBRETE DE VENCIMENTO
    # =====================================================

    @staticmethod
    def mensagem_lembrete(notinha):

        if not notinha:
            raise ValueError(
                "Notinha não encontrada."
            )

        saldo = (
            NotinhaService.saldo_pendente(
                notinha
            )
        )

        if saldo <= 0:
            return None

        hoje = date.today()

        dias_restantes = (
            notinha.data_vencimento
            - hoje
        ).days

        if dias_restantes < 0:
            return None

        cliente_nome = (
            notinha.cliente.nome
            if notinha.cliente
            else "Cliente"
        )

        piscineiro_nome = (
            notinha.piscineiro.nome
            if notinha.piscineiro
            else None
        )

        data_retirada = (
            notinha.data_retirada
            .strftime("%d/%m/%Y")
        )

        data_vencimento = (
            notinha.data_vencimento
            .strftime("%d/%m/%Y")
        )

        valor_formatado = (
            f"{saldo:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        # =================================================
        # PRAZO
        # =================================================

        if dias_restantes == 0:

            texto_prazo = (
                "vence *hoje*"
            )

        elif dias_restantes == 1:

            texto_prazo = (
                "vence *amanhã*"
            )

        else:

            texto_prazo = (
                f"vence em *{dias_restantes} dias*"
            )

        # =================================================
        # HYDRA ENVIA PARA O CLIENTE
        # =================================================

        if (
            notinha.responsavel_cobranca
            == "HYDRA"
        ):

            if piscineiro_nome:

                origem = (
                    f"retirada pelo "
                    f"*{piscineiro_nome}*"
                )

            else:

                origem = (
                    "retirada diretamente na Hydra"
                )

            return (
                f"Olá, *{cliente_nome}*! Tudo bem? 😊\n\n"
                f"Passando apenas para lembrar que a notinha "
                f"{origem}, no dia *{data_retirada}*, "
                f"possui saldo de *R$ {valor_formatado}*.\n\n"
                f"O vencimento é em *{data_vencimento}* e "
                f"{texto_prazo}.\n\n"
                f"Qualquer dúvida, estamos à disposição. 😊"
            )

        # =================================================
        # PISCINEIRO RECEBE O LEMBRETE
        # =================================================

        if (
            notinha.responsavel_cobranca
            == "PISCINEIRO"
        ):

            if not piscineiro_nome:
                return None

            return (
                f"Olá, *{piscineiro_nome}*! Tudo bem? 😊\n\n"
                f"Passando para lembrar que a notinha do seu cliente "
                f"*{cliente_nome}*, retirada no dia "
                f"*{data_retirada}*, possui saldo de "
                f"*R$ {valor_formatado}*.\n\n"
                f"O vencimento é em *{data_vencimento}* e "
                f"{texto_prazo}.\n\n"
                f"Qualquer dúvida, estamos à disposição. 😊"
            )

        return None