# Hydra ERP
# Responsável por: organizar as pendências financeiras,
# cobranças, atrasos e mensagens automáticas.

from collections import defaultdict
from decimal import Decimal

from app.models.notinha import Notinha
from app.services.notinha_service import NotinhaService


class CobrancaService:

    # =========================================================
    # LISTAR PENDÊNCIAS
    # =========================================================

    @staticmethod
    def listar_pendentes():

        notinhas = (
            Notinha.query
            .filter(
                Notinha.status.notin_(
                    ["PAGA", "CANCELADA"]
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

            if saldo <= 0:
                continue


            situacao = (
                NotinhaService.situacao(
                    notinha
                )
            )


            dias_atraso = (
                NotinhaService.dias_atraso(
                    notinha
                )
            )


            mensagem = (
                NotinhaService.mensagem_cobranca(
                    notinha
                )
            )


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
                    situacao,

                "dias_atraso":
                    dias_atraso,

                "mensagem_cobranca":
                    mensagem
            })

        return resultado


    # =========================================================
    # RESUMO
    # =========================================================

    @staticmethod
    def resumo():

        pendentes = (
            CobrancaService.listar_pendentes()
        )

        total_pendente = Decimal("0.00")
        total_vencido = Decimal("0.00")

        quantidade = 0
        quantidade_vencidas = 0


        for dados in pendentes:

            quantidade += 1

            total_pendente += (
                dados["saldo"]
            )


            if (
                dados["dias_atraso"]
                > 0
            ):

                quantidade_vencidas += 1

                total_vencido += (
                    dados["saldo"]
                )


        return {

            "total_pendente":
                total_pendente,

            "total_vencido":
                total_vencido,

            "quantidade":
                quantidade,

            "quantidade_vencidas":
                quantidade_vencidas
        }


    # =========================================================
    # AGRUPAR POR RESPONSÁVEL
    # =========================================================

    @staticmethod
    def agrupar_por_responsavel():

        pendentes = (
            CobrancaService.listar_pendentes()
        )


        hydra = defaultdict(
            list
        )


        piscineiros = defaultdict(
            lambda: {

                "piscineiro":
                    None,

                "clientes":
                    defaultdict(list)
            }
        )


        for dados in pendentes:

            notinha = (
                dados["notinha"]
            )

            cliente = (
                notinha.cliente
            )


            # =================================================
            # HYDRA
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
            # PISCINEIRO
            # =================================================

            if notinha.piscineiro:

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
                # caso não exista piscineiro,
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