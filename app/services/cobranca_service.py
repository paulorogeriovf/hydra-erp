# Hydra ERP
# Responsável por: organizar exclusivamente
# as cobranças vencidas, seus atrasos e mensagens automáticas.

from collections import defaultdict
from decimal import Decimal

from app.models.notinha import Notinha
from app.services.notinha_service import NotinhaService


class CobrancaService:

    # =========================================================
    # LISTAR SOMENTE VENCIDAS
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


            # Ainda está no prazo.
            # Não aparece em Cobranças.
            if dias_atraso <= 0:
                continue


            situacao = (
                NotinhaService.situacao(
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
    # RESUMO DAS COBRANÇAS VENCIDAS
    # =========================================================

    @staticmethod
    def resumo():

        vencidas = (
            CobrancaService.listar_vencidas()
        )


        total_vencido = Decimal(
            "0.00"
        )


        clientes_em_atraso = set()


        maior_atraso = 0


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


        return {

            "total_vencido":
                total_vencido,

            "quantidade_vencidas":
                len(vencidas),

            "clientes_em_atraso":
                len(clientes_em_atraso),

            "maior_atraso":
                maior_atraso
        }


    # =========================================================
    # AGRUPAR POR RESPONSÁVEL
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
            # HYDRA COBRA O CLIENTE
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
            # PISCINEIRO É O RESPONSÁVEL
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
                # joga para cobrança da Hydra.

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