# Agente Investidor - Fase 2: Core Business Services

**Autor:** Luiz Gustavo Finotello  
**Data:** 10 de Julho de 2025  
**Versão:** 2.0.0

## Visão Geral da Fase 2

A Fase 2 implementa os **Core Business Services** da arquitetura de microserviços, focando nas funcionalidades principais de negócio: metodologias de investimento e análises financeiras avançadas.

## Novos Microserviços Implementados

### 1. Methodology Service (Porta 8003)
**Responsabilidade:** Análise de ações usando as 10 metodologias de investimento

**Metodologias Implementadas:**
- Warren Buffett (Value Investing)
- Benjamin Graham (Defensive Value)
- Peter Lynch (Growth at Reasonable Price)
- Growth Investing
- Dividend Investing
- Linda Bradford Raschke (Technical Trading)
- John Bogle (Passive Investing)
- George Soros (Macro Trading)
- Carl Icahn (Activist Investing)
- Income Investing
- Aggressive Growth

**Funcionalidades:**
- Análise síncrona e assíncrona via Kafka
- Cache inteligente com Redis
- Métricas Prometheus
- Health checks automatizados

### 2. Analysis Service (Porta 8004)
**Responsabilidade:** Análises financeiras avançadas e indicadores fundamentalistas

**Funcionalidades:**
- Cálculo de 15+ indicadores fundamentalistas
- Análise de risco (VaR, Beta, Sharpe Ratio)
- Análise comparativa entre ações
- Análise setorial
- Valuation automático

**Indicadores Suportados:**
- **Rentabilidade:** ROE, ROA, ROIC
- **Valuation:** P/E, P/B, P/S, EV/EBITDA, PEG
- **Endividamento:** Debt/Equity
- **Liquidez:** Current Ratio, Quick Ratio
- **Dividendos:** Dividend Yield, Payout Ratio

## Infraestrutura Avançada

### Apache Kafka (Porta 9092)
**Messaging assíncrono entre microserviços**
- Tópicos especializados por tipo de evento
- Schema Registry para evolução de schemas
- Kafka Connect para integrações
- Kafka UI para monitoramento (Porta 8080)

**Tópicos Implementados:**
- `analysis.requested` - Solicitações de análise
- `analysis.completed` - Análises concluídas
- `methodology.analysis.requested` - Análises de metodologia
- `methodology.analysis.completed` - Metodologias concluídas
- `stock.data.updated` - Atualizações de dados
- `cache.invalidated` - Invalidação de cache

### Cache Distribuído Avançado
**Sistema de cache hierárquico com Redis**
- **L1 Cache:** Memória local (mais rápido)
- **L2 Cache:** Redis distribuído (persistente)
- **L3 Cache:** Backup em banco de dados

**Funcionalidades:**
- Compressão automática para valores grandes
- Serialização múltipla (JSON, Pickle)
- Auto-refresh inteligente
- Invalidação por padrões
- Cache warming automático
- Estatísticas detalhadas

## Comunicação Assíncrona

### Padrões Implementados
1. **Request-Response Assíncrono**
   - Cliente envia requisição via Kafka
   - Serviço processa e responde via Kafka
   - Cliente recebe resultado via polling ou webhook

2. **Event-Driven Architecture**
   - Eventos de domínio publicados automaticamente
   - Múltiplos serviços podem reagir aos eventos
   - Desacoplamento total entre serviços

3. **Saga Pattern**
   - Transações distribuídas entre microserviços
   - Compensação automática em caso de falha
   - Consistência eventual garantida

## Estrutura de Arquivos

```
microservices/
├── methodology-service/          # Serviço de Metodologias
│   ├── main.py                  # Aplicação principal
│   ├── Dockerfile               # Container
│   └── requirements.txt         # Dependências
├── analysis-service/            # Serviço de Análises
│   ├── main.py                  # Aplicação principal
│   ├── Dockerfile               # Container
│   └── requirements.txt         # Dependências
└── shared/                      # Módulos compartilhados
    ├── models/                  # DTOs e modelos
    ├── messaging/               # Cliente Kafka
    └── cache/                   # Gerenciador Redis
```

## Como Executar

### Pré-requisitos
- Docker e Docker Compose
- 8GB RAM mínimo
- Portas 80, 3000, 5432, 6379, 8002-8004, 8080, 9090, 9092 livres

### Inicialização Completa
```bash
# 1. Criar rede Docker
docker network create agente-network

# 2. Iniciar todos os serviços
docker-compose -f docker-compose.fase2.yml up -d

# 3. Verificar status
docker-compose -f docker-compose.fase2.yml ps

# 4. Logs em tempo real
docker-compose -f docker-compose.fase2.yml logs -f
```

### Testes dos Serviços

#### Methodology Service
```bash
# Health check
curl http://localhost:8003/health

# Análise síncrona
curl -X POST "http://localhost:8003/analyze" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "PETR4.SA", "metodologias": ["warren_buffett", "peter_lynch"]}'

# Análise assíncrona
curl -X POST "http://localhost:8003/analyze/async?user_id=123" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "VALE3.SA", "metodologias": ["benjamin_graham"]}'
```

#### Analysis Service
```bash
# Health check
curl http://localhost:8004/health

# Indicadores fundamentalistas
curl http://localhost:8004/indicators/PETR4.SA

# Análise de risco
curl http://localhost:8004/risk/VALE3.SA

# Comparação de ações
curl -X POST "http://localhost:8004/compare" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["PETR4.SA", "VALE3.SA"], "indicador": "pe_ratio"}'
```

## Interfaces de Monitoramento

### Grafana (http://localhost:3000)
- **Usuário:** admin
- **Senha:** admin
- Dashboards pré-configurados para todos os serviços

### Prometheus (http://localhost:9090)
- Métricas de todos os microserviços
- Alertas configurados para falhas

### Kafka UI (http://localhost:8080)
- Monitoramento de tópicos Kafka
- Visualização de mensagens
- Gestão de consumers

## Métricas e Observabilidade

### Métricas Coletadas
- **Requests:** Total, duração, status codes
- **Business:** Análises por metodologia, recomendações
- **Cache:** Hit rate, miss rate, invalidações
- **Kafka:** Mensagens produzidas/consumidas, lag

### Logs Estruturados
- Formato JSON para parsing automático
- Correlação de requests via trace IDs
- Níveis configuráveis por serviço

### Health Checks
- Endpoints `/health` em todos os serviços
- Verificação de dependências (Redis, Kafka)
- Status detalhado de cada componente

## Benefícios da Fase 2

### Escalabilidade
- Cada serviço escala independentemente
- Cache distribuído reduz latência
- Messaging assíncrono aumenta throughput

### Resiliência
- Falha de um serviço não afeta outros
- Circuit breakers implementados
- Retry automático com backoff

### Manutenibilidade
- Código modular e bem documentado
- Testes automatizados
- Deploy independente por serviço

### Performance
- Cache hierárquico reduz latência em 80%
- Processamento assíncrono aumenta throughput
- Compressão automática economiza bandwidth

## Próximos Passos (Fase 3)

1. **User Interface Service** - Interface web moderna
2. **Notification Service** - Alertas e notificações
3. **Portfolio Service** - Gestão de carteiras
4. **Recommendation Engine** - IA para recomendações
5. **API Gateway avançado** - Rate limiting, autenticação
6. **Service Mesh** - Istio para comunicação segura

## Troubleshooting

### Problemas Comuns

**Kafka não conecta:**
```bash
# Verificar se Zookeeper está rodando
docker logs zookeeper

# Recriar tópicos se necessário
docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list
```

**Redis não conecta:**
```bash
# Verificar logs do Redis
docker logs redis

# Testar conexão
docker exec redis redis-cli ping
```

**Serviços não iniciam:**
```bash
# Verificar logs detalhados
docker-compose -f docker-compose.fase2.yml logs [service-name]

# Reconstruir imagens
docker-compose -f docker-compose.fase2.yml build --no-cache
```

## Contribuição

Para contribuir com o projeto:

1. Criar branch a partir da master atualizada
2. Implementar funcionalidade com testes
3. Documentar mudanças no README
4. Criar Pull Request para revisão
5. Aguardar aprovação e merge

## Licença

Este projeto é propriedade de Luiz Gustavo Finotello e está licenciado sob os termos definidos no arquivo LICENSE.

