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

## 🙏 Agradecimentos

- Warren Buffett, Benjamin Graham, Peter Lynch e outros grandes investidores pelas metodologias
- Comunidade open source pelas ferramentas utilizadas
- APIs financeiras que fornecem dados em tempo real

---

⭐ Se este projeto te ajudou, considere dar uma estrela no repositório!

