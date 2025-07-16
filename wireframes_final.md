# 📐 Wireframes Completos - Agente Investidor

**Projeto:** Agente Investidor - Arquitetura de Microserviços  
**Autor:** Luiz Gustavo Finotello  
**Data:** 16 de Janeiro de 2025  
**Versão:** 1.0  

---

## 📋 Wireframes Criados

**9 Telas Principais:**

1. Tela de Login
2. Tela de Cadastro
3. Tela Home
4. Dashboard do Mercado
5. Análise de Ações
6. Chat com Agente
7. Metodologias de Investimento
8. Perfil do Investidor
9. Resultados Detalhados

---

## 1. Tela de Login

### 🔐 Estrutura da Tela

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                    📈 AGENTE INVESTIDOR                         │
│                                                                 │
│                                                                 │
│          ┌─────────────────────────────────────────┐            │
│          │                                         │            │
│          │              ENTRAR                     │            │
│          │                                         │            │
│          │  Usuário                                │            │
│          │  [________________________]            │            │
│          │                                         │            │
│          │  Senha                                  │            │
│          │  [________________________]            │            │
│          │                                         │            │
│          │         [  ENTRAR  ]                   │            │
│          │                                         │            │
│          │    Não tem conta? Cadastre-se          │            │
│          │                                         │            │
│          └─────────────────────────────────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Elementos:
- **Cabeçalho:** Logo centralizado "📈 AGENTE INVESTIDOR"
- **Formulário centralizado** com:
  - Campo "Usuário" (obrigatório)
  - Campo "Senha" (obrigatório, com toggle de visibilidade)
  - Botão "ENTRAR" (primário, azul #667eea)
  - Link "Não tem conta? Cadastre-se"

### Funcionalidades:
- Validação de campos obrigatórios
- Autenticação OAuth 2.0
- Feedback visual para erros
- Redirecionamento para Dashboard após login

---

## 2. Tela de Cadastro

### 📝 Estrutura da Tela

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                    📈 AGENTE INVESTIDOR                         │
│                                                                 │
│                                                                 │
│          ┌─────────────────────────────────────────┐            │
│          │                                         │            │
│          │              CADASTRO                   │            │
│          │                                         │            │
│          │  Usuário                                │            │
│          │  [________________________]            │            │
│          │                                         │            │
│          │  E-mail                                 │            │
│          │  [________________________]            │            │
│          │                                         │            │
│          │  Senha                                  │            │
│          │  [________________________]            │            │
│          │                                         │            │
│          │         [  CADASTRAR  ]                │            │
│          │                                         │            │
│          │      Já tem conta? Entrar               │            │
│          │                                         │            │
│          └─────────────────────────────────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Elementos:
- **Cabeçalho:** Logo centralizado "📈 AGENTE INVESTIDOR"
- **Formulário de registro** com:
  - Campo "Usuário" (obrigatório, validação de disponibilidade)
  - Campo "E-mail" (obrigatório, validação de formato)
  - Campo "Senha" (obrigatório, validação de força)
  - Botão "CADASTRAR" (primário, azul #667eea)
  - Link "Já tem conta? Entrar"

### Funcionalidades:
- Verificação de email único
- Validação de força da senha
- Termos de uso (checkbox)
- Redirecionamento para Perfil do Investidor

---

## 3. Tela Home

### 🏠 Estrutura da Tela

```
┌─────────────────────────────────────────────────────────────────┐
│ 📈 Agente Investidor [Home][Dashboard][Análise][Chat][Metodologias] [👤User] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 HERO SECTION                                │ │
│  │                                                             │ │
│  │  Seu Mentor Pessoal em                                     │ │
│  │      INVESTIMENTOS                                         │ │
│  │                                                             │ │
│  │  Baseado nas metodologias dos maiores                      │ │
│  │        investidores do mundo                               │ │
│  │                                                             │ │
│  │  [Analisar Ação] [Chat com Agente]                        │ │
│  │                                                             │ │
│  │                                      ┌─────────────────────┐ │ │
│  │                                      │  10 Metodologias   │ │ │
│  │                                      │  50+ Indicadores   │ │ │
│  │                                      │  Dados Tempo Real  │ │ │
│  │                                      └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│            Baseado nos Maiores Investidores                     │
│                                                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │    👤       │ │    👤       │ │    👤       │ │    👤       │ │
│  │             │ │             │ │             │ │             │ │
│  │Warren       │ │Benjamin     │ │Peter        │ │Dividend     │ │
│  │Buffett      │ │Graham       │ │Lynch        │ │Focus        │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│      © 2025 Agente Investidor - Desenvolvido por Luiz Gustavo Finotello      │
└─────────────────────────────────────────────────────────────────┘
```

### Seções:
1. **Header:** Navegação completa com menu do usuário
2. **Hero Section:** Proposta de valor e estatísticas
3. **Investidores:** Cards dos grandes mestres
4. **Footer:** Informações de copyright

### Funcionalidades:
- CTAs estratégicos (Analisar Ação, Chat)
- Navegação para todas as seções
- Apresentação dos diferenciais

---

## 4. Dashboard do Mercado

### 📊 Estrutura da Tela

```
┌─────────────────────────────────────────────────────────────────┐
│ 📈 Agente Investidor [Home][Dashboard][Análise][Chat][Metodologias] [👤User] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                      Dashboard do Mercado                       │
│                                                                 │
│  ┌─────────────────────────────┐ ┌─────────────────────────────┐ │
│  │    Ibovespa - Últimos 30    │ │    Setores em Destaque      │ │
│  │           dias              │ │                             │ │
│  │                             │ │                             │ │
│  │      [📊 GRÁFICO]          │ │      [📊 GRÁFICO]          │ │
│  │                             │ │                             │ │
│  │                             │ │                             │ │
│  └─────────────────────────────┘ └─────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────┐ ┌─────────────────────────────┐ │
│  │   Top Ações - Maiores Altas │ │   Análise de Volatilidade   │ │
│  │                             │ │                             │ │
│  │      [📊 GRÁFICO]          │ │      [📊 GRÁFICO]          │ │
│  │                             │ │                             │ │
│  └─────────────────────────────┘ └─────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Ações em Destaque                        │ │
│  │ ┌─────┬─────┬─────────┬──────┬────┬──────┬─────────────────┐ │ │
│  │ │Ação │Preço│Variação │Volume│P/E │Score │      Ação       │ │ │
│  │ ├─────┼─────┼─────────┼──────┼────┼──────┼─────────────────┤ │ │
│  │ │     │     │         │      │    │      │                 │ │ │
│  │ │     │     │         │      │    │      │                 │ │ │
│  │ └─────┴─────┴─────────┴──────┴────┴──────┴─────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│                    Indicadores Econômicos                       │
│                                                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │    IPCA     │ │     PIB     │ │ Desemprego  │ │Commodities  │ │
│  │             │ │             │ │             │ │             │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Componentes:
1. **Gráficos de Mercado:** Ibovespa, Setores, Top Ações, Volatilidade
2. **Tabela de Ações:** Dados em tempo real com scores
3. **Indicadores:** IPCA, PIB, Desemprego, Commodities

### Funcionalidades:
- Atualização em tempo real
- Filtros e ordenação
- Exportação de dados
- Personalização do dashboard

---

## 5. Análise de Ações

### 🔍 Estrutura da Tela

```
┌─────────────────────────────────────────────────────────────────┐
│ 📈 Agente Investidor [Home][Dashboard][Análise][Chat][Metodologias] [👤User] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                        Análise de Ações                         │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Selecione a Ação          Metodologia           [ANALISAR]│ │
│  │  [Ex: PETR4, VALE3▼]      [Warren Buffett▼]              │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 Resultados da Análise                       │ │
│  │                                                             │ │
│  │    ┌─────────┐                                             │ │
│  │    │   85    │        ┌─────────────────────┐              │ │
│  │    │         │        │      COMPRA         │              │ │
│  │    │ Score   │        └─────────────────────┘              │ │
│  │    └─────────┘                                             │ │
│  │                                                             │ │
│  │                           Pontos Fortes:                   │ │
│  │                           • ROE > 15%                      │ │
│  │                           • P/E < 20                       │ │
│  │                                                             │ │
│  │  ┌─────────────────────────────┐ ┌─────────────────────────┐ │ │
│  │  │    Histórico de Preços      │ │   Indicadores Técnicos  │ │ │
│  │  │                             │ │                         │ │ │
│  │  │      [📊 GRÁFICO]          │ │     [📊 GRÁFICO]       │ │ │
│  │  │                             │ │                         │ │ │
│  │  └─────────────────────────────┘ └─────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Seções:
1. **Formulário:** Seleção de ação e metodologia
2. **Resultados:** Score, recomendação e pontos fortes
3. **Gráficos:** Histórico de preços e indicadores técnicos

### Funcionalidades:
- Análise baseada em 10 metodologias
- Score de 0-100 com recomendação
- Justificativa detalhada
- Exportação de relatórios

---

## 6. Chat com Agente

### 💬 Estrutura da Tela

```
┌─────────────────────────────────────────────────────────────────┐
│ 📈 Agente Investidor [Home][Dashboard][Análise][Chat][Metodologias] [👤User] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                   Chat com o Agente Investidor                  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                                                             │ │
│  │  ┌─────────────────────────────────────────────────────────┐ │ │
│  │  │ AGENTE: Olá! Como posso ajudá-lo com seus investimentos?│ │ │
│  │  └─────────────────────────────────────────────────────────┘ │ │
│  │                                                             │ │
│  │                  ┌─────────────────────────────────────────┐ │ │
│  │                  │ VOCÊ: Como Warren Buffett analisa ações?│ │ │
│  │                  └─────────────────────────────────────────┘ │ │
│  │                                                             │ │
│  │  ┌─────────────────────────────────────────────────────────┐ │ │
│  │  │ AGENTE: Warren Buffett usa Value Investing, focando em: │ │ │
│  │  │ • Empresas com vantagem competitiva                     │ │ │
│  │  │ • Gestão de qualidade e preço razoável                 │ │ │
│  │  └─────────────────────────────────────────────────────────┘ │ │
│  │                                                             │ │
│  │                        Sugestões:                           │ │
│  │                                                             │ │
│  │  [O que é P/E?]  [Como começar?]  [Análise técnica]       │ │
│  │                                                             │ │
│  │  ┌─────────────────────────────────────────────────────────┐ │ │
│  │  │ Digite sua pergunta...                          [ENVIAR]│ │ │
│  │  └─────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Componentes:
1. **Área de Mensagens:** Conversação com o agente
2. **Sugestões:** Perguntas frequentes e tópicos
3. **Input:** Campo de texto com botão de envio

### Funcionalidades:
- IA conversacional especializada
- Histórico de conversas
- Sugestões inteligentes
- Compartilhamento de análises

---

## 7. Metodologias de Investimento

### 📚 Estrutura da Tela

```
┌─────────────────────────────────────────────────────────────────┐
│ 📈 Agente Investidor [Home][Dashboard][Análise][Chat][Metodologias] [👤User] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                   Metodologias de Investimento                  │
│                                                                 │
│  ┌─────────────────────────────┐ ┌─────────────────────────────┐ │
│  │        Warren Buffett       │ │      Benjamin Graham        │ │
│  │        Value Investing      │ │      Defensive Value        │ │
│  │                             │ │                             │ │
│  │         P/E < 25            │ │         P/E < 15            │ │
│  │         ROE > 15%           │ │         P/B < 1.5           │ │
│  │         D/E < 0.5           │ │    Current Ratio > 2        │ │
│  │                             │ │                             │ │
│  └─────────────────────────────┘ └─────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────┐ ┌─────────────────────────────┐ │
│  │        Peter Lynch          │ │    Foco em Dividendos       │ │
│  │ Growth at Reasonable Price  │ │     Income Investing        │ │
│  │                             │ │                             │ │
│  │         PEG < 1             │ │         DY > 4%             │ │
│  │    Crescimento > 15%        │ │      Payout < 80%           │ │
│  │       Small Caps            │ │         ROE > 12%           │ │
│  │                             │ │                             │ │
│  └─────────────────────────────┘ └─────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Layout:
- **Grid 2x2** com as 4 principais metodologias
- **Cada card contém:**
  - Nome do investidor
  - Tipo de estratégia
  - Indicadores principais
  - Critérios de análise

### Metodologias:
1. **Warren Buffett:** Value Investing
2. **Benjamin Graham:** Defensive Value
3. **Peter Lynch:** Growth at Reasonable Price
4. **Foco em Dividendos:** Income Investing

---

## 8. Perfil do Investidor

### 👤 Estrutura da Tela

```
┌─────────────────────────────────────────────────────────────────┐
│ 📈 Agente Investidor [Home][Dashboard][Análise][Chat][Metodologias] [👤User] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ████████████████████████████████████████████████████████████   │
│  ███                                                      ███   │
│  ███              ┌─────────────────────────────────────┐  ███   │
│  ███              │        Perfil de Investidor        │  ███   │
│  ███              │                                  [X]│  ███   │
│  ███              │                                     │  ███   │
│  ███              │ Qual é o seu principal objetivo     │  ███   │
│  ███              │      com investimentos?             │  ███   │
│  ███              │                                     │  ███   │
│  ███              │  ○ Preservar capital e ter segurança│  ███   │
│  ███              │  ○ Renda passiva através de dividendos│ ███   │
│  ███              │  ○ Crescimento de longo prazo       │  ███   │
│  ███              │  ○ Ganhos rápidos e especulação     │  ███   │
│  ███              │                                     │  ███   │
│  ███              │                                     │  ███   │
│  ███              │                                     │  ███   │
│  ███              │  [ANTERIOR]          [PRÓXIMO]      │  ███   │
│  ███              └─────────────────────────────────────┘  ███   │
│  ███                                                      ███   │
│  ████████████████████████████████████████████████████████████   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Estrutura:
- **Modal centralizado** sobre fundo escuro
- **Questionário interativo** com múltiplas opções
- **Navegação por etapas** (Anterior/Próximo)
- **Botão fechar** (X) no canto superior direito

### Funcionalidades:
- Questionário de tolerância ao risco
- Definição de objetivos de investimento
- Personalização de recomendações
- Classificação automática do perfil

---

## 9. Resultados Detalhados

### 📈 Estrutura da Tela

```
┌─────────────────────────────────────────────────────────────────┐
│ 📈 Agente Investidor [Home][Dashboard][Análise][Chat][Metodologias] [👤User] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                   Análise Detalhada - PETR4                     │
│                                                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────────┐ │
│  │  Score: 85  │ │Preço Atual: │ │ Metodologia: Warren Buffett │ │
│  │   COMPRA    │ │  R$ 32,45   │ │                             │ │
│  └─────────────┘ │Preço Alvo:  │ │                             │ │
│                  │  R$ 42,00   │ │                             │ │
│                  └─────────────┘ └─────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────┐ ┌─────────────────────────────┐ │
│  │  Histórico de Preços (6m)   │ │   Volume de Negociação      │ │
│  │                             │ │                             │ │
│  │      [📊 GRÁFICO]          │ │      [📊 GRÁFICO]          │ │
│  │                             │ │                             │ │
│  │                             │ │                             │ │
│  └─────────────────────────────┘ └─────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Métricas Detalhadas                      │ │
│  │                                                             │ │
│  │  Valuation    Rentabilidade   Endividamento   Crescimento  │ │
│  │                                                             │ │
│  │   P/E: 12.5     ROE: 18%       D/E: 0.3     Receita: 15%  │ │
│  │   P/B: 1.8      ROA: 8%     Current R: 2.1   Lucro: 22%   │ │
│  │ EV/EBITDA: 8.2  ROIC: 12%    Quick R: 1.5     DY: 8%     │ │
│  │                                                             │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 Justificativa da Análise                    │ │
│  │                                                             │ │
│  │  A empresa apresenta fundamentos sólidos com ROE acima de  │ │
│  │  15%, P/E atrativo e baixo endividamento, seguindo os      │ │
│  │  critérios de Warren Buffett.                              │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Seções:
1. **Cabeçalho:** Score, preços e metodologia
2. **Gráficos:** Histórico de preços e volume
3. **Métricas:** Valuation, rentabilidade, endividamento, crescimento
4. **Justificativa:** Análise fundamentalista detalhada

### Funcionalidades:
- Análise completa baseada na metodologia escolhida
- Métricas categorizadas por tipo
- Justificativa técnica
- Recomendações de acompanhamento

---

## 🎨 Design System

### Paleta de Cores:
- **Primária:** #667eea (Azul Agente Investidor)
- **Secundária:** #764ba2 (Roxo complementar)
- **Sucesso:** #28a745 (Verde para recomendações de compra)
- **Aviso:** #ffc107 (Amarelo para alertas)
- **Erro:** #dc3545 (Vermelho para recomendações de venda)
- **Texto:** #333333 (Cinza escuro para texto)
- **Borda:** #e0e0e0 (Cinza claro para bordas)

### Componentes Padronizados:
- **Headers:** Navegação consistente em todas as telas
- **Formulários:** Campos com labels e validação
- **Botões:** Hierarquia visual (primário, secundário)
- **Cards:** Containers informativos com bordas arredondadas
- **Tabelas:** Estrutura de dados organizada
- **Modais:** Sobreposições para formulários e confirmações

---

## 🔄 Fluxos de Navegação

### Fluxo Principal:
```
Login → Home → Dashboard → Análise → Resultados → Chat
```

### Fluxo de Novo Usuário:
```
Cadastro → Perfil do Investidor → Tutorial → Dashboard → Primeira Análise
```

### Fluxo de Análise:
```
Seleção de Ação → Escolha da Metodologia → Análise → Resultados → Ações de Follow-up
```

---

## 📱 Responsividade

### Breakpoints:
- **Mobile:** < 768px
- **Tablet:** 768px - 1024px
- **Desktop:** > 1024px

### Adaptações Mobile:
- Menu hamburger para navegação
- Cards empilhados verticalmente
- Gráficos otimizados para toque
- Formulários com campos maiores
- Botões com área de toque adequada

---

## 🚀 Funcionalidades Implementadas

### Autenticação:
- ✅ Login com validação
- ✅ Cadastro com verificação de email
- ✅ OAuth 2.0 integrado
- ✅ Logout automático por inatividade

### Dashboard:
- ✅ Dados em tempo real da B3
- ✅ Gráficos interativos
- ✅ Indicadores econômicos
- ✅ Tabela de ações com filtros

### Análise:
- ✅ 10 metodologias de investimento
- ✅ 50+ indicadores financeiros
- ✅ Score de 0-100 com justificativa
- ✅ Recomendações automatizadas

### Chat:
- ✅ IA conversacional especializada
- ✅ Histórico de conversas
- ✅ Sugestões inteligentes
- ✅ Integração com análises

---

## 🎯 Próximos Passos

### Implementação:
1. **Criação dos componentes** baseados nos wireframes
2. **Desenvolvimento das APIs** de integração
3. **Testes de usabilidade** com usuários reais
4. **Otimização de performance** para mobile
5. **Integração com corretoras** para dados em tempo real

### Design:
1. **Prototipagem interativa** no Figma
2. **Refinamento visual** com cores e tipografia
3. **Criação de ícones** personalizados
4. **Animações e transições** para melhor UX
5. **Testes A/B** de interface

---

## ✅ Conclusão

Este documento apresenta todos os wireframes necessários para o desenvolvimento da interface do **Agente Investidor**. Cada tela foi projetada considerando:

- **Usabilidade:** Interface intuitiva e acessível
- **Funcionalidade:** Todas as features do sistema cobertas
- **Consistência:** Padrões visuais e de navegação
- **Responsividade:** Adaptação para diferentes dispositivos
- **Escalabilidade:** Estrutura preparada para crescimento

Os wireframes fornecem uma base sólida para o desenvolvimento, garantindo que a interface final atenda aos requisitos do projeto e proporcione uma excelente experiência do usuário.

### 📄 Arquivo Gerado:
**wireframes_final.pdf** - Documento completo com todos os wireframes

---

**Desenvolvido por:** Luiz Gustavo Finotello  
**Data:** 16 de Janeiro de 2025  
**Projeto:** Agente Investidor - Arquitetura de Microserviços