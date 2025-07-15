FROM python:3.11-alpine

WORKDIR /app

# Instalar dependências do sistema
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    freetype-dev \
    && rm -rf /var/cache/apk/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY main.py .

# Criar diretório para relatórios
RUN mkdir -p /tmp/reports

# Expor porta
EXPOSE 8008

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8008/health || exit 1

# Criar grupo e usuário não-root
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# Comando para executar a aplicação
CMD ["python", "main.py"] 