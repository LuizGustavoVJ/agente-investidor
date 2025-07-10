# Dockerfile para Serviço de Metodologias
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Copiar modelos compartilhados
COPY ../shared /app/microservices/shared

# Criar usuário não-root
RUN useradd -m -u 1000 methoduser && chown -R methoduser:methoduser /app
USER methoduser

# Expor porta
EXPOSE 8003

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

# Comando para iniciar
CMD ["python", "main.py"]

