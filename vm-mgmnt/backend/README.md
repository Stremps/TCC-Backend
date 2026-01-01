# TCC Pipeline 3D - Backend & Orquestrador

Este diretório contém a API REST e o serviço de Orquestração do projeto de TCC. O sistema gerencia a criação de jobs de IA generativa, filas de processamento e persistência de metadados.

## 1) Stack Tecnológica

* **Linguagem:** Python 3.11+
* **Framework Web:** FastAPI (ASGI)
* **Gerenciador de Pacotes:** Poetry
* **Banco de Dados:** PostgreSQL (Supabase) via SQLAlchemy Async
* **Migrações:** Alembic
* **Qualidade de Código:** Ruff

## 2) Configuração do Ambiente

### A) Pré-requisitos

Certifique-se de ter instalado:
* Python 3.11 ou superior
* Poetry (Gerenciador de dependências)

### B) Instalação

Instale as dependências do projeto:
```bash
poetry install
```

### C) Variáveis de Ambiente

1. Copie o exemplo para criar seu arquivo de configuração local:```bash
cp .env.example .env

2. Edite o arquivo `.env` e insira a Connection String do Supabase na variável `DATABASE_URL`.
**Importante:** Utilize o driver assíncrono `postgresql+asyncpg://`.

## 3) Banco de Dados

O projeto utiliza SQLAlchemy Async com Alembic para gerenciamento de schema.

### A) Entidades Principais

O banco de dados é centrado no processo de geração (Job-Centric). As principais tabelas são:

* **users:** Usuários e chaves de API (autenticação via x-api-key).
* **models:** Catálogo de IAs disponíveis (ex: sf3d-v1, dreamfusion-sd) com seus parâmetros padrão em JSONB.
* **jobs:** Tabela central que rastreia o ciclo de vida (QUEUED -> RUNNING -> SUCCEEDED) e parâmetros de execução.
* **artifacts:** Referências aos arquivos gerados (Output 3D, Previews, Logs) armazenados no MinIO.
* **job_events:** Log estruturado de eventos para auditoria e métricas.

### B) Gerenciamento de Migrações

Sempre que alterar um modelo em `app/models/`, gere uma nova migração e aplique ao banco:

#### 1 - Criar Revisão

Detecta mudanças automaticamente:
```bash
poetry run alembic revision --autogenerate -m "descricao_da_mudanca"
```

#### 2 - Aplicar Mudanças

Executa o upgrade no banco de dados:
```bash
poetry run alembic upgrade head
```

### C) Inicialização de Dados (Seed)

Para operar o sistema, é necessário popular o banco com os Dados Mestre (Usuário Admin e Modelos de IA suportados). O script é idempotente.

#### 1 - Configurar Credenciais

Certifique-se de que o seu `.env` possui as variáveis do superusuário:
```ini
FIRST_SUPERUSER_USERNAME=admin
FIRST_SUPERUSER_PASSWORD=sua_senha_segura
FIRST_SUPERUSER_API_KEY=sua_chave_estatica
```

#### 2 - Executar o Seed

Rode o script através do módulo da aplicação:
```bash
poetry run python -m app.initial_data
```

O script realizará as seguintes ações:

1. Cria (ou atualiza a senha) do usuário admin definido no .env.
2. Lê o arquivo `app/db/seeds/ai_models.json`.
3. Cria ou atualiza os parâmetros dos modelos de IA no banco.

## 4) Execução e Desenvolvimento

### A) Servidor de Desenvolvimento

Para subir a API com hot-reload (reinicia ao salvar arquivos):
```bash
poetry run uvicorn app.main:app --reload
```

Acesse a documentação automática em: http://127.0.0.1:8000/docs

### B) Qualidade de Código (Linting)

O projeto usa `ruff` para padronização. Para verificar o código:
```bash
poetry run ruff check .```