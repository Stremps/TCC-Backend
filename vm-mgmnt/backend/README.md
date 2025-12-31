# TCC Pipeline 3D - Backend & Orquestrador

Este diretório contém a API REST e o serviço de Orquestração do projeto de TCC.
O sistema gerencia a criação de jobs de IA generativa, filas de processamento e persistência de metadados.

## Stack Tecnológica

- **Linguagem:** Python 3.11+
- **Framework Web:** FastAPI (ASGI)
- **Gerenciador de Pacotes:** Poetry
- **Banco de Dados:** PostgreSQL (Supabase) via SQLAlchemy Async
- **Migrações:** Alembic
- **Qualidade de Código:** Ruff

## Pré-requisitos

Certifique-se de ter instalado:
- Python 3.11 ou superior
- [Poetry](https://python-poetry.org/docs/#installation)

## Instalação e Configuração

1. **Instale as dependências:**
   ```bash
   poetry install