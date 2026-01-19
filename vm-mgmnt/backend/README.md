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

1. Copie o exemplo para criar seu arquivo de configuração local:
```bash
cp .env.example .env
```

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
poetry run ruff check .
```

---

## 5) API Reference (Endpoints)

A API segue o padrão **RESTful**. Todos os endpoints são prefixados com `/api/v1`.

### A) Autenticação
Todas as rotas exigem autenticação via Header.
* **Header:** `x-api-key`
* **Valor:** Sua chave de API

### B) Criar Job de Geração
Inicia um novo processo de geração 3D. A resposta é imediata (assíncrona) e devolve um ID para acompanhamento.

* **Rota:** `POST /jobs/`
* **Status Sucesso:** `201 Created`

#### 1. Corpo da Requisição (JSON)

| Campo | Tipo | Obrigatório | Descrição |
| :--- | :--- | :---: | :--- |
| `model_id` | `string` | Sim | ID do modelo (ex: `sf3d-v1`, `dreamfusion-sd`). |
| `input_params` | `dict` | Sim | Parâmetros específicos do modelo (resolução, steps). |
| `prompt` | `string` | Não | Obrigatório apenas para modelos Text-to-3D. |

**Exemplo de Request:**
```json
{
  "model_id": "sf3d-v1",
  "input_params": {
    "texture_resolution": 1024,
    "foreground_ratio": 0.85
  }
}
```

**Exemplo de Resposta:**

```json
{
  "id": "a1b2c3d4-1234-5678-90ab-cdef12345678",
  "model_id": "sf3d-v1",
  "status": "QUEUED",
  "created_at": "2025-12-31T20:00:00.123456",
  "input_params": { ... }
}
```

### C) Consultar Status (Polling)

Busca os detalhes atualizados de um Job. Utilize este endpoint periodicamente (ex: a cada 2s) para verificar se o status mudou de `QUEUED` para `SUCCEEDED`.

* **Rota:** `GET /jobs/{job_id}`
* **Status Sucesso:** `200 OK`
* **Erros Comuns:** `404` (Não encontrado) ou `403` (Sem permissão).

**Exemplo de Resposta:**

```json
{
  "id": "a1b2c3d4-1234-5678-90ab-cdef12345678",
  "status": "SUCCEEDED",
  "progress_percent": 100,
  "created_at": "2025-12-31T20:00:00.000000",
  "started_at": "2025-12-31T20:00:05.000000",
  "completed_at": "2025-12-31T20:00:15.000000",
  "model_id": "sf3d-v1",
  "input_params": { ... }
}
```

### D) Download do Artefato

Gera uma URL temporária e segura (**Presigned URL**) para baixar o arquivo 3D final diretamente do Storage. O link possui validade de 1 hora.

* **Rota:** `GET /jobs/{job_id}/download`
* **Status Sucesso:** `200 OK`
* **Pré-requisito:** O Job deve estar com status `SUCCEEDED`.
* **Erros Comuns:** `400` (Job ainda não finalizado) ou `404` (Arquivo não encontrado).

**Exemplo de Resposta:**

```json
{
  "download_url": "[http://192.168.1.181:9000/tcc-pipeline/jobs/...?X-Amz-Signature=](http://192.168.1.181:9000/tcc-pipeline/jobs/...?X-Amz-Signature=)...",
  "expires_in": 3600
}
```

---

## 6) Como rodar o Worker

Para receber os trabalhos da fila, o worker terá um script específico para ele. Mas isso estará nos arquivos de VM-IA, por favor consultar para entender melhor.

## 7) Monitorar Fila (Dashboard)

Interface visual para ver jobs e falhas. Depois de deixar rodando, acesse em `http://localhost:9181`

```bash
poetry run rq-dashboard
```

## Documentação Interativa (Swagger UI)

Para testar a API visualmente e ver todos os schemas detalhados, acesse com o servidor rodando:

* **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Arquitetura do Backend

Este projeto utiliza uma arquitetura baseada em eventos para processamento assíncrono de tarefas pesadas (Geração 3D).

* **API (FastAPI):** Responsável por receber requisições, autenticação e leitura de dados. Opera de forma 100% assíncrona (`asyncio`).
* **Worker (RQ):** Processo separado responsável por executar a IA e tarefas de I/O intensivo. Opera de forma síncrona e híbrida.
* **Broker (Redis):** Gerencia a fila de tarefas entre API e Worker.
* **Storage (MinIO):** Armazena os arquivos grandes (modelos 3D, texturas) gerados.

---

## 3) Variáveis de Ambiente (.env)

Crie um arquivo `.env` na raiz desta pasta baseado no `.env.example`. Abaixo, a explicação detalhada de cada variável crítica para a infraestrutura.

### A) Banco de Dados (Postgres)
| Variável | Descrição | Exemplo |
| :--- | :--- | :--- |
| `DATABASE_URL` | String de conexão SQLAlchemy (Async). | `postgresql+asyncpg://user:pass@host:5432/db` |

### B) Segurança e Acesso (CORS)
Controle de quais domínios podem consumir a API (Frontend).
| Variável | Descrição | Exemplo |
| :--- | :--- | :--- |
| `BACKEND_CORS_ORIGINS` | Lista de origens permitidas separadas por vírgula. | `http://localhost:3000,http://editor-3d.com` |

### C) Fila de Tarefas (Redis)
Necessário para comunicação entre API e Workers.
| Variável | Descrição | Exemplo |
| :--- | :--- | :--- |
| `REDIS_URL` | Endereço do broker Redis. | `redis://localhost:6379/0` |

### D) Object Storage (MinIO / S3)
Configuração para upload de artefatos gerados.
| Variável | Descrição | Exemplo |
| :--- | :--- | :--- |
| `MINIO_ENDPOINT` | URL da API do MinIO (não do Console). | `http://192.168.1.181:9000` |
| `MINIO_ACCESS_KEY` | Chave de acesso (ou usuário root em dev). | `admin` |
| `MINIO_SECRET_KEY` | Chave secreta (ou senha root em dev). | `password` |
| `MINIO_BUCKET` | Nome do bucket para salvar arquivos. | `tcc-pipeline` |
| `MINIO_SECURE` | Define se usa HTTPS (`True`) ou HTTP (`False`). | `False` |

## 4) Fluxo de Upload e Consumo (API)

Para garantir escalabilidade e evitar sobrecarga no servidor de aplicação, o sistema utiliza o padrão de **Presigned URLs** (Ticket Pattern). A API não recebe arquivos binários diretamente.

### A) Workflow de Criação de Job (Com Upload)

1.  **Solicitar Ticket:** O cliente (Frontend) requisita permissão de upload.
    * `POST /api/v1/jobs/upload-ticket`
    * Body: `{"filename": "textura.png", "content_type": "image/png"}`
    * Response: Retorna uma `upload_url` (assinada) e um `object_name`.

2.  **Upload Direto:** O cliente envia o arquivo binário diretamente para o Storage (MinIO) usando a `upload_url`.
    * Método: `PUT`
    * Header: `Content-Type: image/png`

3.  **Criar Job:** O cliente confirma a criação do job enviando o caminho do arquivo.
    * `POST /api/v1/jobs/`
    * Body: `{"model_id": "sf3d-v1", "input_params": {"image_path": "object_name_recebido_no_passo_1"}}`

**Nota:** O artefato de input só é registrado na tabela `artifacts` se o Job for criado com sucesso (consistência atômica).

### B) Segurança (CORS)

O Backend implementa um Middleware de segurança que intercepta todas as requisições.
* **Allowlist:** Apenas origens listadas em `BACKEND_CORS_ORIGINS` recebem os headers `Access-Control-Allow-Origin`.
* **Credenciais:** O sistema permite `allow_credentials=True`, suportando autenticação via Cookies/Headers seguros entre domínios distintos (ex: Frontend em localhost:3000 e API em localhost:8000).