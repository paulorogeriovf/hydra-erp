# 🌊 Hydra ERP

Sistema de gestão desenvolvido para centralizar e organizar processos operacionais, financeiros e comerciais da **Hydra Piscinas e Lazer**.

O projeto foi desenvolvido em **Python com Flask e MySQL**, com foco inicialmente em utilização local na empresa, permitindo reunir em um único sistema informações que antes estavam distribuídas entre diferentes controles e ferramentas.

> 🚧 Projeto em desenvolvimento e aprimoramento contínuo.

---

## 🎯 Objetivo

O Hydra ERP tem como objetivo facilitar a gestão das principais operações da empresa, principalmente o relacionamento entre:

* Clientes
* Piscineiros
* Produtos
* Notinhas
* Pagamentos
* Comissões
* Cobranças
* Vendas
* Histórico de movimentações

O sistema também utiliza os dados registrados para gerar indicadores comerciais e identificar oportunidades de vendas.

---

## ⚙️ Principais funcionalidades

### 📊 Dashboard

Visão geral da operação com indicadores como:

* vendas do mês;
* vendas dos últimos meses;
* ticket médio;
* valores a receber;
* valores vencidos;
* notinhas pendentes;
* cobranças próximas;
* comissões disponíveis;
* produtos mais vendidos;
* piscineiros com maior volume de vendas;
* oportunidades comerciais;
* movimentações recentes.

---

### 🏊 Piscineiros

Cadastro e gerenciamento dos piscineiros parceiros.

Cada piscineiro possui uma página própria contendo informações como:

* clientes vinculados;
* histórico de vendas;
* notinhas;
* comissões;
* produtos mais vendidos;
* indicadores financeiros;
* evolução mensal.

---

### 👥 Clientes

Gerenciamento dos clientes da empresa.

O sistema permite:

* cadastrar clientes;
* editar informações;
* ativar ou desativar cadastros;
* vincular cliente a um piscineiro;
* alterar o piscineiro responsável;
* consultar histórico;
* visualizar movimentações financeiras e compras.

O histórico da relação entre cliente e piscineiro é preservado.

---

### 📦 Produtos

Catálogo central de produtos utilizado pelos demais módulos do ERP.

Informações disponíveis:

* nome;
* marca;
* categoria;
* preço normal;
* preço de atacado;
* geração de comissão;
* percentual de comissão;
* observações;
* status.

---

### 📄 Notinhas

Controle de vendas realizadas por meio de notinhas.

As notinhas podem ser organizadas por:

* piscineiro;
* clientes diretos da Hydra.

Cada registro pode possuir:

* cliente;
* produtos;
* valores;
* data de retirada;
* vencimento;
* observações;
* responsável pela cobrança;
* pagamentos;
* pagamentos parciais;
* fotos;
* comprovantes;
* anexos.

O sistema calcula automaticamente valores pagos e pendentes e identifica notinhas vencidas.

---

### 💰 Comissões

Controle das comissões destinadas aos piscineiros.

O sistema registra:

* comissão gerada;
* comissão retirada;
* saldo disponível;
* origem da comissão;
* histórico de retiradas.

A comissão é calculada somente para produtos configurados para gerar comissão.

---

### 📅 Cobranças

Área destinada ao acompanhamento financeiro das notinhas.

Apresenta separadamente:

* cobranças vencidas;
* cobranças próximas do vencimento.

O sistema também auxilia na preparação de mensagens de cobrança ou lembrete para envio aos responsáveis.

---

### 🧾 Gerador de Orçamentos

Gerador integrado ao catálogo de produtos do ERP.

Permite:

* selecionar produtos;
* informar quantidades;
* aplicar desconto;
* informar cliente;
* gerar orçamento;
* copiar texto;
* gerar PDF.

---

### 📈 Inteligência de Vendas

Utiliza o histórico cadastrado no ERP para apresentar rankings e indicadores comerciais.

Inclui:

* produtos mais vendidos;
* clientes que mais compram;
* piscineiros com maior volume de vendas;
* ticket médio;
* vendas mensais;
* clientes atendidos.

---

### 💡 Oportunidades de Vendas

Análise do histórico de compras para identificar possíveis oportunidades.

O sistema considera o comportamento de compra dos clientes para localizar:

* produtos que normalmente eram comprados e estão atrasados em relação ao padrão;
* clientes que estão há mais tempo sem comprar do que seu comportamento histórico indica.

Essa análise ganha precisão conforme o ERP acumula histórico real de utilização.

---

### 📜 Histórico

Registro das principais movimentações realizadas no sistema.

Entre elas:

* criação e alteração de clientes;
* alteração de piscineiros;
* alterações de produtos;
* criação de notinhas;
* pagamentos;
* comissões;
* demais movimentações relevantes.

---

### ⚙️ Configurações

Área destinada aos dados cadastrais da empresa.

Permite armazenar e copiar rapidamente informações como:

* razão social;
* nome fantasia;
* CNPJ;
* inscrição estadual;
* inscrição municipal;
* telefone;
* WhatsApp;
* e-mail;
* endereço;
* dados bancários;
* chave PIX;
* responsável.

---

### 💾 Backup

O Hydra ERP possui geração de backup pelo próprio sistema.

O backup reúne:

```text
hydra_backup_DATA_HORA.zip
│
├── banco/
│   └── hydra_erp.sql
│
└── uploads/
    └── notinhas/
        └── ...
```

São protegidos:

* banco de dados MySQL;
* fotos das notinhas;
* comprovantes;
* anexos enviados ao ERP.

Os arquivos de backup não são versionados no Git.

---

## 🛠️ Tecnologias

### Backend

* Python
* Flask
* Flask-SQLAlchemy
* SQLAlchemy
* Flask-Migrate

### Banco de dados

* MySQL
* PyMySQL

### Frontend

* HTML
* CSS
* JavaScript
* Jinja2
* Chart.js

### Outras ferramentas

* Git
* GitHub
* MySQL Workbench
* VS Code

---

## 📁 Estrutura do projeto

```text
hydra-erp/
│
├── app/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── static/
│   ├── templates/
│   ├── __init__.py
│   └── extensions.py
│
├── data/
│   └── uploads/
│
├── backups/
│
├── docs/
├── migrations/
│
├── .env
├── .gitignore
├── config.py
├── requirements.txt
└── run.py
```

Arquivos operacionais, uploads, backups e credenciais não são enviados ao repositório.

---

## 🚀 Instalação para desenvolvimento

### 1. Clone o repositório

```bash
git clone https://github.com/paulorogeriovf/hydra-erp.git
```

Entre na pasta:

```bash
cd hydra-erp
```

### 2. Crie o ambiente virtual

Windows:

```bash
python -m venv .venv
```

Ative:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o `.env`

Crie um arquivo `.env` na raiz do projeto.

Exemplo:

```env
SECRET_KEY=sua_chave_secreta
DATABASE_URL=mysql+pymysql://usuario:senha@localhost/nome_do_banco
```

> Nunca envie o arquivo `.env` para o GitHub.

### 5. Configure o MySQL

Crie o banco que será utilizado pela aplicação e configure sua conexão no `DATABASE_URL`.

### 6. Execute as migrations

```bash
flask --app run.py db upgrade
```

### 7. Inicie o ERP

```bash
flask --app run.py run
```

A aplicação estará disponível localmente pelo endereço informado pelo Flask.

---

## 🔐 Segurança dos dados

O repositório não deve conter:

* `.env`;
* credenciais do banco;
* fotos reais;
* comprovantes;
* arquivos enviados pelos usuários;
* backups do banco de dados.

Esses arquivos estão separados do código-fonte e protegidos pelo `.gitignore`.

---

## 🗺️ Estado atual

O Hydra ERP já possui os principais módulos funcionais e atualmente está em fase de:

* validação com dados reais;
* testes de backup e restauração;
* revisão final de fluxos;
* melhorias de usabilidade;
* preparação para utilização na operação real.

Funcionalidades de usuários, login e permissões poderão ser adicionadas futuramente caso o sistema passe a ser utilizado por múltiplos usuários ou dispositivos.

---

## 📚 Contexto do projeto

Além de atender uma necessidade real de gestão da Hydra Piscinas e Lazer, o Hydra ERP é utilizado como projeto de aprendizado e aplicação prática de conceitos de:

* Engenharia de Software;
* Programação Orientada a Objetos;
* Banco de Dados;
* Desenvolvimento Web;
* Arquitetura de Sistemas;
* Segurança da Informação;
* análise de dados.

---

## 👨‍💻 Autor

**Paulo Rogério**

Projeto Hydra ERP.

---

## 📌 Status

**Em desenvolvimento.**

O sistema ainda está sendo validado antes de sua utilização definitiva em ambiente operacional.
