# Dockerfile para Serviço de Dados Externos
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends --fix-missing \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Criar usuário não-root
RUN useradd -m -u 1000 datauser && chown -R datauser:datauser /app
USER datauser

# Expor porta
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Comando para iniciar
CMD ["python", "main.py"]

ENV PYTHONPATH="${PYTHONPATH}:/app:/app/microservices"

