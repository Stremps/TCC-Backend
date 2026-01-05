# ==========================================
# ESTÁGIO 1: Builder (Gera o requirements.txt)
# ==========================================
FROM python:3.13-slim as builder

# Evita que o Python gere arquivos .pyc e garante logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /tmp

# Instala utilitários de sistema básicos
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# CORREÇÃO AQUI: Instala poetry E o plugin de export
RUN pip install poetry poetry-plugin-export

# Copia apenas os arquivos de dependência primeiro (para usar cache do Docker)
COPY pyproject.toml poetry.lock* /tmp/

# Exporta as dependências do Poetry para um requirements.txt padrão
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --without dev

# ==========================================
# ESTÁGIO 2: Runner (Imagem Final Leve)
# ==========================================
FROM python:3.13-slim

WORKDIR /app

# Variáveis de ambiente para otimização
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Instala dependências de sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copia o requirements.txt do estágio anterior
COPY --from=builder /tmp/requirements.txt /app/requirements.txt

# Instala as dependências Python no sistema do container
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copia o código da aplicação
COPY ./app /app/app

# Expõe a porta que o Uvicorn vai usar
EXPOSE 8000

# Comando de execução (Produção)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]