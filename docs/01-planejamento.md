hydra-erp/
│
├── app/
│   ├── __init__.py
│   ├── extensions.py
│   │
│   ├── models/
│   │   └── __init__.py
│   │
│   ├── routes/
│   │   └── __init__.py
│   │
│   ├── services/
│   │   └── __init__.py
│   │
│   ├── templates/
│   │   └── base.html
│   │
│   └── static/
│       ├── css/
│       ├── js/
│       └── img/
│
├── data/
│   └── uploads/
│       └── notinhas/
│
├── docs/
│   ├── 01-planejamento.md
│   ├── 02-regras-de-negocio.md
│   ├── 03-modelagem-banco.md
│   ├── 04-configuracao-ambiente.md
│   └── 05-diario-desenvolvimento.md
│
├── migrations/
├── tests/
│
├── .env
├── .gitignore
├── config.py
├── requirements.txt
└── run.py

# Configuração inicial do ambiente — Hydra ERP

## 1. Objetivo

Preparar o ambiente de desenvolvimento necessário para a implementação do sistema Hydra ERP, utilizando Python e Flask no backend e MySQL como sistema gerenciador de banco de dados.

## 2. Tecnologias definidas

Foram definidas inicialmente as seguintes tecnologias:

* Python para desenvolvimento do backend;
* Flask como framework web;
* MySQL como sistema gerenciador de banco de dados;
* MySQL Workbench para administração e visualização do banco;
* HTML, CSS e JavaScript para a interface;
* Git e GitHub para versionamento do código-fonte.

## 3. Instalação do MySQL

Foi instalado o MySQL Installer 8.0.46.

Durante a instalação, foi utilizada a configuração personalizada (`Custom`), permitindo selecionar apenas os componentes necessários ao ambiente de desenvolvimento.

Foram instalados os principais componentes:

* MySQL Server;
* MySQL Workbench;
* MySQL Shell.

Durante a configuração do servidor foi definida uma senha administrativa para o usuário `root`.

Por questões de segurança, a senha não deve ser registrada nesta documentação nem armazenada no repositório Git.

## 4. Criação do banco de desenvolvimento

Após a instalação, foi realizada a conexão ao servidor local utilizando o MySQL Workbench.

Foi criado um banco específico para o ambiente de desenvolvimento:

```sql
CREATE DATABASE hydra_erp_dev;
```

A criação foi verificada utilizando:

```sql
SHOW DATABASES;
```

O banco `hydra_erp_dev` apareceu entre os bancos disponíveis no servidor.

## 5. Usuário da aplicação

Foi decidido que o Hydra ERP não utilizará diretamente o usuário administrativo `root`.

Foi criado um usuário específico para a aplicação:

```text
hydra_app
```

Esse usuário recebeu permissões sobre o banco:

```text
hydra_erp_dev
```

A separação entre o usuário administrativo e o usuário utilizado pela aplicação reduz o uso desnecessário de privilégios administrativos.

## 6. Separação dos ambientes

O banco utilizado durante o desenvolvimento será:

```text
hydra_erp_dev
```

Posteriormente, no computador servidor da empresa, será utilizado um banco destinado ao ambiente de produção, mantendo os ambientes separados.

## 7. Versionamento

O código-fonte do Hydra ERP será versionado utilizando Git e armazenado no GitHub.

Informações sensíveis e dados operacionais não serão enviados ao repositório, incluindo:

* senhas;
* arquivo `.env`;
* banco de dados de produção;
* fotografias das notinhas;
* backups;
* arquivos enviados pelos usuários.

Esses itens serão protegidos por configurações apropriadas no `.gitignore` e por mecanismos próprios de backup.

## 8. Resultado da etapa

Ao final desta etapa, o MySQL Server encontra-se instalado e funcionando, o banco de desenvolvimento `hydra_erp_dev` foi criado e um usuário específico foi preparado para futura comunicação entre a aplicação Flask e o banco de dados.


Flask
→ aplicação web

Flask-SQLAlchemy
→ Python ↔ banco

Flask-Migrate
→ migrations

python-dotenv
→ lê nosso .env

PyMySQL
→ driver Python ↔ MySQL

pip install Flask Flask-SQLAlchemy Flask-Migrate python-dotenv PyMySQL