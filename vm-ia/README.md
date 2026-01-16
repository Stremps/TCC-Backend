
# TCC Worker - AI Processing Unit

Microsserviço responsável pelo processamento pesado (CPU/GPU) das tarefas de geração 3D.
Este componente opera de forma **síncrona** e isolada, consumindo tarefas da fila Redis e interagindo com modelos de IA.

## 1) Arquitetura

O Worker foi desacoplado da API principal para permitir: Isolamento de Dependências; Escala; Resiliência.

**Fluxo de Trabalho:**
1.  Escuta a fila `default` no Redis.
2.  Recebe um Job com parâmetros (`input_params`).
3.  Invoca o Wrapper da IA correspondente (ex: `sf3d`, `dreamfusion`).
4.  Faz upload do resultado (`.glb`) para o MinIO.
5.  Atualiza o status no Banco de Dados (`SUCCEEDED`/`FAILED`).

## 2) Configuração

### 1. Pré-requisitos
* Python 3.11+
* Acesso à rede das VMs de Gestão (`vm-mgmnt`) e Storage (`vm-storage`).

### 2. Variáveis de Ambiente
Crie um arquivo `.env` baseado no exemplo:
```bash
cp .env.example .env
```

Preencha com os IPs corretos da sua infraestrutura:

* `REDIS_URL`: Onde a fila está rodando.
* `DATABASE_URL`: Onde o PostgreSQL está rodando.
* `MINIO_*`: Credenciais do Object Storage.

### 3. Instalação

Utilizamos **Poetry** para gerenciamento de dependências.

```bash
poetry install

```

---

## 3) Como Rodar

Diferente do uso padrão do CLI `rq worker`, utilizamos um script Python customizado para garantir o carregamento correto das configurações (Pydantic/DotEnv).

**Comando de Execução:**

```bash
poetry run python run_worker.py
```

---

## 📂 Estrutura de IAs (Wrappers)

Para facilitar a integração de novos modelos, utilizamos o padrão de **Wrappers**. Cada modelo fica em sua própria pasta dentro de `wrappers/`:

* `wrappers/sf3d/`: Lógica para o modelo Stable Fast 3D.
* `wrappers/dreamfusion/`: Lógica para o modelo DreamFusion.

O `app/worker.py` atua apenas como um "gerente", delegando a execução técnica para esses scripts.

Consulte o README dentro da pasta `wrappers/` para detalhes técnicos sobre os parâmetros de entrada e saída de cada modelo.


