<<<<<<< HEAD
# Agente Investidor - Arquitetura de Microserviços

**Autor:** Luiz Gustavo Finotello  
**Versão:** 1.0.0  
**Data:** 10 de Julho de 2025  

## Visão Geral

Este projeto implementa a Fase 1 da migração do Agente Investidor para uma arquitetura de microserviços, conforme documentação técnica detalhada. A implementação inclui containerização, infraestrutura básica, e os dois primeiros microserviços: Autenticação e Dados Externos.

## Arquitetura Implementada

### Microserviços Ativos

1. **Auth Service** (Porta 8001)
   - Autenticação e autorização
   - JWT tokens
   - Gerenciamento de usuários
   - Métricas Prometheus

2. **Data Service** (Porta 8002)
   - Integração com APIs externas (Yahoo Finance)
   - Cache inteligente com Redis
   - Rate limiting
   - Normalização de dados

### Infraestrutura

- **API Gateway**: Nginx (Porta 80)
- **Banco de Dados**: PostgreSQL (Porta 5432)
- **Cache**: Redis (Porta 6379)
- **Monitoramento**: Prometheus (Porta 9090) + Grafana (Porta 3000)
- **Logs**: ELK Stack (Elasticsearch:9200, Kibana:5601)

## Início Rápido

### Pré-requisitos

- Docker e Docker Compose instalados
- Git
- 8GB RAM disponível
- Portas 80, 3000, 5432, 6379, 8001, 8002, 9090 livres

### Instalação

1. **Clonar repositório:**
```bash
git clone https://github.com/LuizGustavoVJ/agente-investidor.git
cd agente-investidor-microservices
```

2. **Iniciar infraestrutura básica:**
```bash
# Apenas banco e cache
docker-compose up -d postgres redis

# Aguardar inicialização
sleep 10
```

3. **Iniciar microserviços:**
```bash
# Serviços de negócio
docker-compose -f docker-compose.microservices.yml up -d auth-service data-service

# Verificar saúde dos serviços
curl http://localhost:8001/health
curl http://localhost:8002/health
```

4. **Iniciar monitoramento:**
```bash
# Stack de observabilidade
docker-compose -f docker-compose.microservices.yml up -d prometheus grafana elasticsearch kibana
```

5. **Iniciar API Gateway:**
```bash
# Gateway e aplicação principal
docker-compose -f docker-compose.microservices.yml up -d api-gateway agente-investidor
```

### Verificação da Instalação

1. **Serviços de Saúde:**
```bash
curl http://localhost/health                    # API Gateway
curl http://localhost:8001/health              # Auth Service
curl http://localhost:8002/health              # Data Service
```

2. **Interfaces Web:**
- **Aplicação Principal**: http://localhost
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Kibana**: http://localhost:5601

## Uso dos Microserviços

### Auth Service

**Registrar usuário:**
```bash
curl -X POST http://localhost:8001/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "first_name": "João",
    "last_name": "Silva"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8001/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

**Validar token:**
```bash
curl -X POST http://localhost:8001/validate \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Data Service

**Obter dados de ação:**
```bash
curl http://localhost:8002/stock/PETR4.SA
```

**Dados históricos:**
```bash
curl http://localhost:8002/stock/PETR4.SA/history?period=1mo
```

**Múltiplas ações:**
```bash
curl "http://localhost:8002/stocks/batch?symbols=PETR4.SA,VALE3.SA,ITUB4.SA"
```

**Índices de mercado:**
```bash
curl http://localhost:8002/market/indices
```

### Via API Gateway

Todos os serviços também estão disponíveis via API Gateway:

```bash
# Auth via gateway
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Data via gateway
curl http://localhost/api/data/stock/PETR4.SA
```

## Monitoramento

### Métricas Prometheus

- **Auth Service**: http://localhost:8001/metrics
- **Data Service**: http://localhost:8002/metrics
- **Prometheus UI**: http://localhost:9090

### Dashboards Grafana

Acesse http://localhost:3000 (admin/admin) para visualizar:
- Performance dos microserviços
- Métricas de negócio
- Saúde da infraestrutura

### Logs Centralizados

- **Kibana**: http://localhost:5601
- **Elasticsearch**: http://localhost:9200

## Desenvolvimento

### Estrutura do Projeto

```
agente-investidor-microservices/
├── services/
│   ├── auth-service/           # Serviço de Autenticação
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── data-service/           # Serviço de Dados
│       ├── main.py
│       ├── requirements.txt
│       └── Dockerfile
├── infrastructure/
│   ├── databases/              # Scripts SQL
│   ├── monitoring/             # Prometheus, Grafana
│   └── nginx/                  # API Gateway
├── docker-compose.yml          # Infraestrutura básica
├── docker-compose.microservices.yml  # Microserviços
└── README.md
```

### Adicionando Novos Serviços

1. Criar diretório em `services/`
2. Implementar FastAPI com estrutura similar
3. Adicionar ao `docker-compose.microservices.yml`
4. Configurar rotas no Nginx
5. Adicionar métricas Prometheus

### Hot Reload

Os serviços suportam hot reload durante desenvolvimento:

```bash
# Logs em tempo real
docker-compose -f docker-compose.microservices.yml logs -f auth-service data-service
```

## Testes

### Testes de Carga

```bash
# Instalar Apache Bench
sudo apt-get install apache2-utils

# Teste auth service
ab -n 1000 -c 10 -H "Content-Type: application/json" \
   -p auth_payload.json http://localhost:8001/login

# Teste data service
ab -n 1000 -c 10 http://localhost:8002/stock/PETR4.SA
```

### Testes de Integração

```bash
# Script de teste completo
./scripts/integration_tests.sh
```

## Próximos Passos (Fase 2)

1. **Serviço de Metodologias**: Migrar 10 estratégias de investimento
2. **Serviço de Análises**: Indicadores fundamentalistas
3. **Message Broker**: Apache Kafka para comunicação assíncrona
4. **Service Mesh**: Istio para comunicação avançada

## Troubleshooting

### Problemas Comuns

**Serviços não iniciam:**
```bash
# Verificar logs
docker-compose logs auth-service
docker-compose logs data-service

# Verificar portas
netstat -tulpn | grep :8001
```

**Cache não funciona:**
```bash
# Verificar Redis
docker-compose exec redis redis-cli ping

# Limpar cache
curl -X DELETE http://localhost:8002/cache/PETR4.SA
```

**Métricas não aparecem:**
```bash
# Verificar Prometheus targets
curl http://localhost:9090/api/v1/targets
```

### Logs Úteis

```bash
# Todos os serviços
docker-compose -f docker-compose.microservices.yml logs

# Serviço específico
docker-compose -f docker-compose.microservices.yml logs -f auth-service

# Nginx access logs
docker-compose -f docker-compose.microservices.yml exec api-gateway tail -f /var/log/nginx/access.log
```

## Contribuição

1. Fork do projeto
2. Criar branch para feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit das mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para branch (`git push origin feature/nova-funcionalidade`)
5. Criar Pull Request

## Licença

Este projeto está sob licença MIT. Veja arquivo LICENSE para detalhes.

## Contato

**Luiz Gustavo Finotello**  
Email: finotello22@hotmail.com  
GitHub: https://github.com/LuizGustavoVJ
=======
# 🚀 Agente Investidor

**Seu mentor pessoal no mundo dos investimentos**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Sobre o Projeto

O **Agente Investidor** é uma aplicação web inteligente que funciona como mentor pessoal no mundo dos investimentos. Baseado nas metodologias dos maiores investidores da história como Warren Buffett, Benjamin Graham, Peter Lynch e estratégias focadas em dividendos, o sistema oferece análises fundamentalistas profissionais, educação financeira interativa e recomendações personalizadas.

### 🎯 Objetivo

Democratizar o acesso ao conhecimento de investimentos de alta qualidade, fornecendo análises baseadas em metodologias comprovadas e dados em tempo real dos mercados financeiros brasileiros e internacionais.

## ✨ Funcionalidades

### 📊 Análise Fundamentalista
- **4 Metodologias Implementadas**: Warren Buffett, Benjamin Graham, Peter Lynch e Foco em Dividendos
- **Indicadores Financeiros**: P/E, ROE, PEG, Dividend Yield, Debt-to-Equity e mais
- **Sistema de Pontuação**: Scores de 0-100 com recomendações COMPRA/VENDA/NEUTRO
- **Preços-Alvo**: Estimativas baseadas nas metodologias escolhidas

### 🤖 Chat Inteligente
- **Mentor Virtual**: Explica conceitos de investimento de forma didática
- **Base de Conhecimento**: Informações sobre grandes investidores e suas estratégias
- **Sugestões Interativas**: Perguntas frequentes para facilitar o aprendizado

### 🎨 Interface Moderna
- **Design Responsivo**: Funciona perfeitamente em desktop e mobile
- **Navegação Intuitiva**: Interface limpa e profissional
- **Feedback Visual**: Animações e transições suaves

### 📈 Dados em Tempo Real
- **APIs Financeiras**: Integração com Yahoo Finance para dados atualizados
- **Mercado Brasileiro**: Suporte completo a ações da B3
- **Mercados Internacionais**: Análise de ações americanas e globais

## 🧠 Metodologias Implementadas

### 1. Warren Buffett - Value Investing
- Foco em empresas com vantagem competitiva sustentável
- Critérios: P/E < 25, ROE > 15%, D/E < 0.5, FCF positivo
- Filosofia: Longo prazo, gestão de qualidade

### 2. Benjamin Graham - Defensive Value
- Segurança do principal e margem de segurança
- Critérios: P/E < 15, P/B < 1.5, Current Ratio > 2
- Filosofia: Conservador, proteção contra perdas

### 3. Peter Lynch - Growth at Reasonable Price
- Crescimento a preço razoável
- Critérios: PEG < 1, crescimento > 15%, empresas conhecidas
- Filosofia: "Invista no que você conhece"

### 4. Foco em Dividendos - Income Investing
- Renda passiva através de dividendos
- Critérios: DY > 4%, Payout < 80%, ROE > 12%
- Filosofia: Empresas maduras com distribuição consistente

## 🚀 Como Executar

### Pré-requisitos
- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)
- Git

### Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/LuizGustavoVJ/agente-investidor.git
cd agente-investidor
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Execute a aplicação**
```bash
python src/main.py
```

5. **Acesse no navegador**
```
http://localhost:5000
```

## 💻 Tecnologias Utilizadas

### Backend
- **Python 3.11**: Linguagem principal
- **Flask 3.1**: Framework web minimalista
- **Flask-CORS**: Suporte a Cross-Origin Resource Sharing
- **Requests**: Cliente HTTP para APIs externas

### Frontend
- **HTML5**: Estrutura semântica
- **CSS3**: Estilização moderna com Grid e Flexbox
- **JavaScript ES6+**: Lógica de interação
- **Font Awesome**: Ícones vetoriais
- **Google Fonts**: Tipografia profissional

### APIs e Dados
- **Yahoo Finance API**: Dados de ações e mercados
- **B3 Data**: Informações do mercado brasileiro

## 📁 Estrutura do Projeto

```
agente_investidor/
├── src/
│   ├── main.py                 # Aplicação principal Flask
│   ├── models/
│   │   ├── investidor.py       # Metodologias dos investidores
│   │   ├── analise_financeira.py # Cálculos e análises
│   │   └── user.py            # Modelo de usuário
│   ├── routes/
│   │   ├── agente.py          # Rotas da API do agente
│   │   └── user.py            # Rotas de usuário
│   └── static/
│       ├── index.html         # Interface principal
│       ├── styles.css         # Estilos CSS
│       └── script.js          # Lógica JavaScript
├── requirements.txt           # Dependências do projeto
├── test_apis.py              # Script de testes das APIs
└── README.md                 # Este arquivo
```

## 🧪 Testes

Para testar as APIs financeiras:

```bash
python test_apis.py
```

## 📖 Exemplos de Uso

### Análise de Ação Brasileira
```
Símbolo: PETR4.SA
Metodologia: Warren Buffett
Resultado: Score 75/100, Recomendação COMPRA
```

### Análise de Ação Americana
```
Símbolo: AAPL
Metodologia: Benjamin Graham
Resultado: Score 65/100, Recomendação NEUTRO
```

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👨‍💻 Autor

**Luiz Gustavo Finotello**
- Email: finotello22@hotmail.com
- GitHub: [@LuizGustavoVJ](https://github.com/LuizGustavoVJ)


---

⭐ Se este projeto te ajudou, considere dar uma estrela no repositório!
>>>>>>> e7a5c56278d56013fb1d0a0f51f23ed83d4b914b

