# TCC Worker - Unidade de Processamento de IA

Microsserviço responsável pelo processamento pesado (CPU/GPU) das tarefas de geração 3D.
Este componente opera de forma **síncrona** e isolada, consumindo tarefas da fila Redis e interagindo com modelos de IA via CLI Wrappers.

## 1. Arquitetura

O Worker foi desacoplado da API principal para permitir: Isolamento de Dependências, Escala Horizontal e Resiliência.

**Fluxo de Trabalho:**
1.  O processo escuta a fila `default` no Redis.
2.  Ao receber um Job, cria um diretório temporário isolado.
3.  Realiza o download dos insumos (imagens) do Object Storage (MinIO).
4.  Invoca o Wrapper da IA correspondente (ex: `sf3d`, `dreamfusion`) via subprocesso.
5.  Realiza o upload do resultado (`.glb` ou `.obj`) para o MinIO.
6.  Registra o artefato e atualiza o status no Banco de Dados.

## 2. Configuração

### 2.1. Pré-requisitos
* Python 3.11+
* Acesso à rede das VMs de Gestão (`vm-mgmnt`) e Storage (`vm-storage`).
* Modelos de IA instalados na máquina host (com seus respectivos ambientes virtuais configurados).

### 2.2. Variáveis de Ambiente
Crie um arquivo `.env` na raiz baseado no exemplo `.env.example`. As variáveis são divididas em Infraestrutura e Caminhos dos Modelos.

#### Infraestrutura
| Variável | Descrição |
| :--- | :--- |
| `REDIS_URL` | String de conexão do Redis (ex: redis://192.168.1.180:6379/0) |
| `DATABASE_URL` | String de conexão do PostgreSQL (ex: postgresql+asyncpg://...) |
| `MINIO_ENDPOINT` | URL do MinIO (ex: http://192.168.1.181:9000) |
| `MINIO_ACCESS_KEY` | Chave de acesso do MinIO |
| `MINIO_SECRET_KEY` | Chave secreta do MinIO |
| `MINIO_BUCKET` | Nome do bucket para inputs/outputs (ex: tcc-pipeline) |

#### Wrappers de IA (Caminhos Absolutos)
É crucial que estes caminhos apontem corretamente para os ambientes virtuais e scripts clonados na máquina host.

| Variável | Descrição |
| :--- | :--- |
| `SF3D_PYTHON_PATH` | Caminho do executável Python dentro do venv do Stable Fast 3D |
| `SF3D_SCRIPT_PATH` | Caminho do script `run.py` do repositório Stable Fast 3D |
| `DREAMFUSION_PYTHON_PATH` | Caminho do executável Python dentro do venv do Threestudio |
| `DREAMFUSION_SCRIPT_PATH` | Caminho do script `launch.py` do repositório Threestudio |
| `DREAMFUSION_CONFIG` | Caminho relativo da config base (ex: configs/dreamfusion-sd.yaml) |

## 3. Instalação e Execução

Utilizamos **Poetry** para gerenciamento de dependências.

```bash
# Instalar dependências
poetry install
```

### Execução do Worker

Utilize o script customizado `run_worker.py` que garante o carregamento correto das configurações antes de iniciar o loop do RQ.

```bash
poetry run python run_worker.py
```

## 4. Estrutura de Wrappers

Para evitar conflitos de dependências entre o orquestrador e os modelos de IA (Dependency Hell), utilizamos o padrão de **Process Isolation**. O Worker invoca os modelos como processos externos.

* `wrappers/sf3d/`: Lógica de encapsulamento para Image-to-3D.
* `wrappers/dreamfusion/`: Lógica de encapsulamento para Text-to-3D.

Cada diretório de wrapper possui seu próprio `run.py` que atua como interface CLI padronizada.