# Hydra ERP
# Responsável por: centralizar os models utilizados pela aplicação.

from app.models.produto import Produto

from app.models.piscineiro import Piscineiro
from app.models.cliente import Cliente
from app.models.historico_piscineiro_cliente import HistoricoPiscineiroCliente

from app.models.notinha import Notinha
from app.models.item_notinha import ItemNotinha
from app.models.pagamento import Pagamento
from app.models.anexo_notinha import AnexoNotinha
from app.models.observacao_notinha import ObservacaoNotinha

from app.models.retirada_comissao import RetiradaComissao

from app.models.movimentacao import Movimentacao