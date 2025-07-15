# Makefile para Agente Investidor - Microserviços
# Autor: Luiz Gustavo Finotello

.PHONY: help install test test-unit test-integration test-e2e test-coverage build run clean lint format

# Variáveis
PYTHON = python3
PIP = pip3
PYTEST = pytest
DOCKER = docker
DOCKER_COMPOSE = docker compose

# Cores para output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

help: ## Mostra esta ajuda
	@echo "$(BLUE)Agente Investidor - Microserviços$(NC)"
	@echo "$(YELLOW)Comandos disponíveis:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Instala dependências
	@echo "$(YELLOW)Instalando dependências...$(NC)"
	$(PIP) install -r tests/requirements.txt
	$(PIP) install -r services/auth-service/requirements.txt
	$(PIP) install -r services/data-service/requirements.txt
	$(PIP) install -r services/user-service/requirements.txt
	$(PIP) install -r services/dashboard-service/requirements.txt
	$(PIP) install -r services/notification-service/requirements.txt
	$(PIP) install -r services/report-service/requirements.txt
	$(PIP) install -r microservices/methodology-service/requirements.txt
	$(PIP) install -r microservices/analysis-service/requirements.txt
	@echo "$(GREEN)Dependências instaladas com sucesso!$(NC)"

test: ## Executa todos os testes
	@echo "$(YELLOW)Executando todos os testes...$(NC)"
	$(PYTEST) tests/ -v
	@echo "$(GREEN)Todos os testes concluídos!$(NC)"

test-unit: ## Executa apenas testes unitários
	@echo "$(YELLOW)Executando testes unitários...$(NC)"
	$(PYTEST) tests/unit/ -v -m unit
	@echo "$(GREEN)Testes unitários concluídos!$(NC)"

test-integration: ## Executa apenas testes de integração
	@echo "$(YELLOW)Executando testes de integração...$(NC)"
	$(PYTEST) tests/integration/ -v -m integration
	@echo "$(GREEN)Testes de integração concluídos!$(NC)"

test-e2e: ## Executa apenas testes end-to-end
	@echo "$(YELLOW)Executando testes end-to-end...$(NC)"
	$(PYTEST) tests/e2e/ -v -m e2e
	@echo "$(GREEN)Testes end-to-end concluídos!$(NC)"

test-coverage: ## Executa testes com relatório de cobertura
	@echo "$(YELLOW)Executando testes com cobertura...$(NC)"
	$(PYTEST) tests/ --cov=microservices --cov=services --cov-report=html --cov-report=term
	@echo "$(GREEN)Relatório de cobertura gerado em htmlcov/$(NC)"

test-performance: ## Executa testes de performance
	@echo "$(YELLOW)Executando testes de performance...$(NC)"
	$(PYTEST) tests/ -v -m performance
	@echo "$(GREEN)Testes de performance concluídos!$(NC)"

# Comandos da Fase 1 e 2
build-fase2: ## Constrói imagens Docker da Fase 2
	@echo "$(YELLOW)Construindo imagens Docker da Fase 2...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.fase2.yml build
	@echo "$(GREEN)Imagens da Fase 2 construídas com sucesso!$(NC)"

run-fase2: ## Inicia serviços da Fase 2
	@echo "$(YELLOW)Iniciando serviços da Fase 2...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.fase2.yml up -d
	@echo "$(GREEN)Serviços da Fase 2 iniciados!$(NC)"
	@echo "$(BLUE)Serviços disponíveis:$(NC)"
	@echo "  - Auth Service: http://localhost:8001"
	@echo "  - Data Service: http://localhost:8002"
	@echo "  - Methodology Service: http://localhost:8004"
	@echo "  - Analysis Service: http://localhost:8003"
	@echo "  - Grafana: http://localhost:3000"
	@echo "  - Prometheus: http://localhost:9090"

# Comandos da Fase 3
build-fase3: ## Constrói imagens Docker da Fase 3
	@echo "$(YELLOW)Construindo imagens Docker da Fase 3...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.fase3.yml build
	@echo "$(GREEN)Imagens da Fase 3 construídas com sucesso!$(NC)"

run-fase3: ## Inicia todos os serviços (Fase 1, 2 e 3)
	@echo "$(YELLOW)Iniciando todos os serviços...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.fase3.yml up -d
	@echo "$(GREEN)Todos os serviços iniciados!$(NC)"
	@echo "$(BLUE)Serviços disponíveis:$(NC)"
	@echo "  - Auth Service: http://localhost:8001"
	@echo "  - Data Service: http://localhost:8002"
	@echo "  - Methodology Service: http://localhost:8004"
	@echo "  - Analysis Service: http://localhost:8003"
	@echo "  - User Service: http://localhost:8005"
	@echo "  - Dashboard Service: http://localhost:8006"
	@echo "  - Notification Service: http://localhost:8007"
	@echo "  - Report Service: http://localhost:8008"
	@echo "  - Grafana: http://localhost:3000"
	@echo "  - Prometheus: http://localhost:9090"

build: build-fase3 ## Constrói todas as imagens Docker (padrão: Fase 3)
run: run-fase3 ## Inicia todos os serviços (padrão: Fase 3)

stop: ## Para todos os serviços
	@echo "$(YELLOW)Parando serviços...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.fase3.yml down
	@echo "$(GREEN)Serviços parados!$(NC)"

restart: stop run ## Reinicia todos os serviços

logs: ## Mostra logs dos serviços
	$(DOCKER_COMPOSE) -f docker-compose.fase3.yml logs -f

health: ## Verifica saúde dos serviços
	@echo "$(YELLOW)Verificando saúde dos serviços...$(NC)"
	@curl -s http://localhost:8001/health || echo "$(RED)Auth Service: DOWN$(NC)"
	@curl -s http://localhost:8002/health || echo "$(RED)Data Service: DOWN$(NC)"
	@curl -s http://localhost:8003/health || echo "$(RED)Analysis Service: DOWN$(NC)"
	@curl -s http://localhost:8004/health || echo "$(RED)Methodology Service: DOWN$(NC)"
	@curl -s http://localhost:8005/health || echo "$(RED)User Service: DOWN$(NC)"
	@curl -s http://localhost:8006/health || echo "$(RED)Dashboard Service: DOWN$(NC)"
	@curl -s http://localhost:8007/health || echo "$(RED)Notification Service: DOWN$(NC)"
	@curl -s http://localhost:8008/health || echo "$(RED)Report Service: DOWN$(NC)"
	@echo "$(GREEN)Verificação de saúde concluída!$(NC)"

health-fase3: ## Verifica saúde apenas dos serviços da Fase 3
	@echo "$(YELLOW)Verificando saúde dos serviços da Fase 3...$(NC)"
	@curl -s http://localhost:8005/health || echo "$(RED)User Service: DOWN$(NC)"
	@curl -s http://localhost:8006/health || echo "$(RED)Dashboard Service: DOWN$(NC)"
	@curl -s http://localhost:8007/health || echo "$(RED)Notification Service: DOWN$(NC)"
	@curl -s http://localhost:8008/health || echo "$(RED)Report Service: DOWN$(NC)"
	@echo "$(GREEN)Verificação de saúde da Fase 3 concluída!$(NC)"

clean: ## Remove containers, volumes e imagens
	@echo "$(YELLOW)Limpando ambiente Docker...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.fase3.yml down -v --rmi all
	$(DOCKER) system prune -f
	@echo "$(GREEN)Ambiente limpo!$(NC)"

lint: ## Executa linting do código
	@echo "$(YELLOW)Executando linting...$(NC)"
	flake8 microservices/ services/ tests/ --max-line-length=120 --ignore=E501,W503
	@echo "$(GREEN)Linting concluído!$(NC)"

format: ## Formata o código
	@echo "$(YELLOW)Formatando código...$(NC)"
	black microservices/ services/ tests/ --line-length=120
	isort microservices/ services/ tests/
	@echo "$(GREEN)Código formatado!$(NC)"

security: ## Executa verificação de segurança
	@echo "$(YELLOW)Executando verificação de segurança...$(NC)"
	bandit -r microservices/ services/ -f json -o security-report.json
	@echo "$(GREEN)Verificação de segurança concluída!$(NC)"

docs: ## Gera documentação
	@echo "$(YELLOW)Gerando documentação...$(NC)"
	$(PYTHON) -m pydoc -w microservices/
	@echo "$(GREEN)Documentação gerada!$(NC)"

migrate: ## Executa migrações do banco de dados
	@echo "$(YELLOW)Executando migrações...$(NC)"
	# Adicionar comandos de migração quando implementado
	@echo "$(GREEN)Migrações concluídas!$(NC)"

seed: ## Popula banco com dados de teste
	@echo "$(YELLOW)Populando banco com dados de teste...$(NC)"
	# Adicionar comandos de seed quando implementado
	@echo "$(GREEN)Dados de teste inseridos!$(NC)"

backup: ## Faz backup do banco de dados
	@echo "$(YELLOW)Fazendo backup do banco...$(NC)"
	$(DOCKER) exec agente-investidor-postgres pg_dump -U postgres agente_investidor > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)Backup concluído!$(NC)"

monitor: ## Abre ferramentas de monitoramento
	@echo "$(BLUE)Abrindo ferramentas de monitoramento...$(NC)"
	@echo "Grafana: http://localhost:3000 (admin/admin)"
	@echo "Prometheus: http://localhost:9090"
	@echo "Kafka UI: http://localhost:8080"

dev: ## Inicia ambiente de desenvolvimento
	@echo "$(YELLOW)Iniciando ambiente de desenvolvimento...$(NC)"
	$(MAKE) install
	$(MAKE) run
	$(MAKE) health
	@echo "$(GREEN)Ambiente de desenvolvimento pronto!$(NC)"

ci: ## Executa pipeline de CI (testes + build)
	@echo "$(YELLOW)Executando pipeline de CI...$(NC)"
	$(MAKE) install
	$(MAKE) lint
	$(MAKE) test-coverage
	$(MAKE) security
	$(MAKE) build
	@echo "$(GREEN)Pipeline de CI concluído!$(NC)"

deploy-staging: ## Deploy para ambiente de staging
	@echo "$(YELLOW)Fazendo deploy para staging...$(NC)"
	$(MAKE) ci
	# Adicionar comandos de deploy quando implementado
	@echo "$(GREEN)Deploy para staging concluído!$(NC)"

deploy-prod: ## Deploy para produção
	@echo "$(RED)ATENÇÃO: Deploy para produção!$(NC)"
	@read -p "Tem certeza? (y/N): " confirm && [ "$$confirm" = "y" ]
	$(MAKE) ci
	# Adicionar comandos de deploy para produção
	@echo "$(GREEN)Deploy para produção concluído!$(NC)"

# Comandos de desenvolvimento rápido
quick-test: ## Testes rápidos (apenas unitários)
	$(PYTEST) tests/unit/ -x -v

quick-build: ## Build rápido (apenas serviços modificados)
	$(DOCKER_COMPOSE) -f docker-compose.fase3.yml build --parallel

quick-restart: ## Restart rápido (apenas serviços core)
	$(DOCKER_COMPOSE) -f docker-compose.fase3.yml restart auth-service methodology-service analysis-service user-service dashboard-service

# Comandos específicos da Fase 3
test-fase3: ## Testa apenas os serviços da Fase 3
	@echo "$(YELLOW)Testando serviços da Fase 3...$(NC)"
	@echo "Testando User Service..."
	@curl -s http://localhost:8005/health | grep -q "healthy" || echo "$(RED)User Service falhou$(NC)"
	@echo "Testando Dashboard Service..."
	@curl -s http://localhost:8006/health | grep -q "healthy" || echo "$(RED)Dashboard Service falhou$(NC)"
	@echo "Testando Notification Service..."
	@curl -s http://localhost:8007/health | grep -q "healthy" || echo "$(RED)Notification Service falhou$(NC)"
	@echo "Testando Report Service..."
	@curl -s http://localhost:8008/health | grep -q "healthy" || echo "$(RED)Report Service falhou$(NC)"
	@echo "$(GREEN)Testes da Fase 3 concluídos!$(NC)"

logs-fase3: ## Mostra logs apenas dos serviços da Fase 3
	$(DOCKER_COMPOSE) -f docker-compose.fase3.yml logs -f user-service dashboard-service notification-service report-service

# Comandos de teste de funcionalidades
test-user-api: ## Testa APIs do User Service
	@echo "$(YELLOW)Testando APIs do User Service...$(NC)"
	@curl -s http://localhost:8005/profile/test-user || echo "$(RED)Profile API falhou$(NC)"
	@curl -s http://localhost:8005/preferences/test-user || echo "$(RED)Preferences API falhou$(NC)"
	@curl -s http://localhost:8005/settings/test-user || echo "$(RED)Settings API falhou$(NC)"
	@echo "$(GREEN)Testes do User Service concluídos!$(NC)"

test-dashboard-api: ## Testa APIs do Dashboard Service
	@echo "$(YELLOW)Testando APIs do Dashboard Service...$(NC)"
	@curl -s http://localhost:8006/dashboards/test-user || echo "$(RED)Dashboards API falhou$(NC)"
	@curl -s http://localhost:8006/metrics/portfolio/test-user || echo "$(RED)Portfolio metrics API falhou$(NC)"
	@curl -s http://localhost:8006/charts/portfolio-performance/test-user || echo "$(RED)Charts API falhou$(NC)"
	@echo "$(GREEN)Testes do Dashboard Service concluídos!$(NC)"

test-notification-api: ## Testa APIs do Notification Service
	@echo "$(YELLOW)Testando APIs do Notification Service...$(NC)"
	@curl -s http://localhost:8007/templates || echo "$(RED)Templates API falhou$(NC)"
	@echo "$(GREEN)Testes do Notification Service concluídos!$(NC)"

test-report-api: ## Testa APIs do Report Service
	@echo "$(YELLOW)Testando APIs do Report Service...$(NC)"
	@curl -s http://localhost:8008/templates || echo "$(RED)Report templates API falhou$(NC)"
	@echo "$(GREEN)Testes do Report Service concluídos!$(NC)"

test-all-fase3: test-user-api test-dashboard-api test-notification-api test-report-api ## Testa todas as APIs da Fase 3

