# Hydra ERP
# Responsável por: centralizar os Blueprints e rotas da aplicação.

from app.routes.dashboard import dashboard_bp
from app.routes.produtos import produtos_bp
from app.routes.piscineiros import piscineiros_bp
from app.routes.clientes import clientes_bp
from app.routes.orcamentos import orcamentos_bp
from app.routes.notinhas import notinhas_bp
from app.routes.cobrancas import cobrancas_bp
from app.routes.comissoes import comissoes_bp
from app.routes.historico import historico_bp
from app.routes.inteligencia_vendas import inteligencia_vendas_bp