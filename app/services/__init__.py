# Hydra ERP
# Responsável por: centralizar os serviços e regras de negócio do sistema.

from app.services.produto_service import ProdutoService
from app.services.piscineiro_service import PiscineiroService
from app.services.cliente_service import ClienteService

from app.services.notinha_service import NotinhaService
from app.services.pagamento_service import PagamentoService

from app.services.observacao_notinha_service import ObservacaoNotinhaService
from app.services.anexo_notinha_service import AnexoNotinhaService