# 📐 Wireframes - Agente Investidor

**Projeto:** Agente Investidor - Arquitetura de Microserviços  
**Autor:** Luiz Gustavo Finotello  
**Data:** 16 de Janeiro de 2025  
**Versão:** 1.0  

## 📋 Visão Geral

Este documento apresenta os wireframes completos para todas as telas do sistema **Agente Investidor**, uma plataforma de análise de investimentos baseada nas metodologias dos maiores investidores do mundo.

### 🎯 Objetivo dos Wireframes

Os wireframes foram criados para:
- **Definir a estrutura** visual e funcional de cada tela
- **Padronizar a interface** seguindo princípios de UX/UI
- **Facilitar o desenvolvimento** fornecendo um guia visual claro
- **Garantir consistência** em toda a aplicação

## 🏗️ Arquitetura da Interface

### Estrutura Base
- **Header:** Navegação principal com menu e área do usuário
- **Main Content:** Conteúdo principal de cada tela
- **Footer:** Informações de copyright e links úteis
- **Modais:** Sobreposições para formulários e confirmações

### Paleta de Cores
- **Primária:** #667eea (Azul principal)
- **Secundária:** #764ba2 (Roxo complementar)
- **Sucesso:** #28a745 (Verde para ações positivas)
- **Aviso:** #ffc107 (Amarelo para alertas)
- **Erro:** #dc3545 (Vermelho para erros)
- **Texto:** #333333 (Cinza escuro)
- **Borda:** #e0e0e0 (Cinza claro)

---

## 📱 Detalhamento das Telas

### 1. 🔐 Tela de Login

**Arquivo:** `wireframes_agente_investidor_otimizado.pdf` - Página 1

#### Elementos:
- **Formulário centralizado** com campos de usuário e senha
- **Botão de login** em destaque
- **Links para cadastro** e recuperação de senha
- **Branding** do Agente Investidor

#### Funcionalidades:
- Validação de campos obrigatórios
- Feedback visual para erros
- Redirecionamento após login bem-sucedido
- Opção de "Lembrar-me"

#### Fluxo:
```
[Usuário acessa] → [Preenche dados] → [Clica "Entrar"] → [Validação] → [Dashboard]
```

---

### 2. 📝 Tela de Cadastro

**Arquivo:** `wireframes_agente_investidor_otimizado.pdf` - Página 2

#### Elementos:
- **Formulário de registro** com usuário, email e senha
- **Validação em tempo real** dos campos
- **Termos de uso** e política de privacidade
- **Botão de cadastro** principal

#### Funcionalidades:
- Verificação de email único
- Validação de força da senha
- Confirmação de senha
- Integração com OAuth (Google, GitHub)

#### Fluxo:
```
[Usuário acessa] → [Preenche formulário] → [Valida dados] → [Cria conta] → [Perfil Investidor]
```

---

### 3. 🏠 Tela Home (Landing Page)

**Arquivo:** `wireframes_agente_investidor_otimizado.pdf` - Página 3

#### Seções:
1. **Hero Section**
   - Título principal e proposta de valor
   - Botões de ação (Analisar Ação, Chat)
   - Estatísticas do sistema

2. **Seção de Investidores**
   - Cards dos grandes investidores
   - Metodologias disponíveis
   - Breve descrição de cada abordagem

3. **Footer**
   - Informações de copyright
   - Links úteis e recursos

#### Funcionalidades:
- Navegação para diferentes seções
- CTAs (Call to Action) estratégicos
- Responsividade para dispositivos móveis

---

### 4. 📊 Dashboard do Mercado

**Arquivo:** `wireframes_agente_investidor_otimizado.pdf` - Página 4

#### Componentes:
1. **Gráficos de Mercado**
   - Ibovespa (últimos 30 dias)
   - Setores em destaque
   - Top ações (altas/baixas)
   - Análise de volatilidade

2. **Tabela de Ações**
   - Ações em destaque
   - Preços e variações
   - Scores de análise
   - Ações rápidas (Analisar, Favoritar)

3. **Indicadores Econômicos**
   - IPCA, PIB, Desemprego
   - Commodities
   - Mini-gráficos de tendência

#### Funcionalidades:
- Atualização em tempo real
- Filtros e ordenação
- Exportação de dados
- Personalização do dashboard

---

### 5. 🔍 Análise de Ações

**Arquivo:** `wireframes_agente_investidor_otimizado.pdf` - Página 5

#### Seções:
1. **Formulário de Análise**
   - Seleção de ação (dropdown com busca)
   - Escolha da metodologia
   - Botão de análise

2. **Resultados da Análise**
   - Score circular (0-100)
   - Recomendação (Compra/Venda/Neutro)
   - Pontos fortes e fracos
   - Justificativa detalhada

3. **Gráficos Complementares**
   - Histórico de preços
   - Indicadores técnicos
   - Comparação com índices

#### Funcionalidades:
- Análise baseada em 10 metodologias
- Exportação de relatórios
- Histórico de análises
- Alertas de preço

---

### 6. 💬 Chat com Agente

**Arquivo:** `wireframes_agente_investidor_otimizado.pdf` - Página 6

#### Componentes:
1. **Área de Mensagens**
   - Mensagens do agente (lado esquerdo)
   - Mensagens do usuário (lado direito)
   - Timestamps e status de leitura

2. **Sugestões Rápidas**
   - Perguntas frequentes
   - Tópicos relacionados
   - Ações rápidas

3. **Input de Mensagem**
   - Campo de texto expansível
   - Botão de envio
   - Indicador de digitação

#### Funcionalidades:
- IA conversacional especializada
- Histórico de conversas
- Busca em mensagens
- Compartilhamento de análises

---

### 7. 📚 Metodologias de Investimento

**Arquivo:** `wireframes_agente_investidor_otimizado.pdf` - Página 7

#### Layout:
- **Grid de Cards** (2x2) com as metodologias
- **Cada Card contém:**
  - Nome do investidor
  - Tipo de estratégia
  - Indicadores principais
  - Critérios de análise

#### Metodologias Incluídas:
1. **Warren Buffett** - Value Investing
2. **Benjamin Graham** - Defensive Value
3. **Peter Lynch** - Growth at Reasonable Price
4. **Foco em Dividendos** - Income Investing

#### Funcionalidades:
- Detalhamento de cada metodologia
- Comparação entre estratégias
- Histórico de performance
- Recomendações personalizadas

---

### 8. 👤 Perfil do Investidor

**Arquivo:** `wireframes_agente_investidor_otimizado.pdf` - Página 8

#### Estrutura:
- **Modal centralizado** sobre fundo escuro
- **Questionário interativo** com múltiplas opções
- **Navegação por etapas** (Anterior/Próximo)
- **Progresso visual** das perguntas

#### Funcionalidades:
- Questionário de tolerância ao risco
- Definição de objetivos
- Personalização de recomendações
- Atualização de perfil

#### Fluxo:
```
[Novo usuário] → [Questionário] → [Análise do perfil] → [Recomendações personalizadas]
```

---

### 9. 📈 Resultados Detalhados

**Arquivo:** `wireframes_agente_investidor_otimizado.pdf` - Página 9

#### Seções:
1. **Cabeçalho da Análise**
   - Score e recomendação
   - Preços atual e alvo
   - Metodologia utilizada

2. **Gráficos Avançados**
   - Histórico de preços (6 meses)
   - Volume de negociação
   - Indicadores técnicos

3. **Métricas Detalhadas**
   - **Valuation:** P/E, P/B, EV/EBITDA
   - **Rentabilidade:** ROE, ROA, ROIC
   - **Endividamento:** D/E, Current Ratio
   - **Crescimento:** Receita, Lucro, Dividend Yield

4. **Justificativa**
   - Análise fundamentalista
   - Pontos de atenção
   - Recomendações de acompanhamento

---

## 🔄 Fluxos de Navegação

### Fluxo Principal
```
Login → Home → Dashboard → Análise → Resultados → Chat (suporte)
```

### Fluxo de Novo Usuário
```
Cadastro → Perfil do Investidor → Tutorial → Dashboard → Primeira Análise
```

### Fluxo de Análise
```
Seleção de Ação → Escolha da Metodologia → Análise → Resultados → Ações (Salvar, Compartilhar, Nova Análise)
```

---

## 📱 Responsividade

### Breakpoints Sugeridos:
- **Mobile:** < 768px
- **Tablet:** 768px - 1024px
- **Desktop:** > 1024px

### Adaptações Mobile:
- Menu hamburger para navegação
- Cards empilhados verticalmente
- Gráficos otimizados para toque
- Formulários com campos maiores

---

## 🎨 Componentes Reutilizáveis

### Componentes Base:
- **Botões:** Primário, Secundário, Texto
- **Formulários:** Input, Select, Radio, Checkbox
- **Cards:** Informação, Métrica, Investidor
- **Modais:** Confirmação, Formulário, Informação
- **Navegação:** Breadcrumb, Tabs, Pagination

### Componentes Específicos:
- **Score Circle:** Visualização de pontuação
- **Chart Container:** Wrapper para gráficos
- **Stock Table:** Tabela de ações otimizada
- **Chat Bubble:** Mensagens do chat
- **Methodology Card:** Card de metodologia

---

## 🔒 Considerações de Segurança

### Autenticação:
- Campos de senha com toggle de visibilidade
- Validação de força da senha
- Proteção contra força bruta
- Logout automático por inatividade

### Autorização:
- Controle de acesso por perfil
- Proteção de rotas sensíveis
- Validação de permissões
- Logs de auditoria

---

## 📊 Métricas e Analytics

### Eventos a Trackear:
- Login/Logout de usuários
- Análises realizadas por metodologia
- Tempo de sessão
- Funcionalidades mais utilizadas
- Conversões (cadastro → primeira análise)

### Dashboards Sugeridos:
- Usuários ativos
- Análises por período
- Performance das metodologias
- Engagement no chat

---

## 🚀 Próximos Passos

### Fase 1: Implementação Base
- [ ] Estrutura HTML/CSS das telas
- [ ] Componentes React/Vue
- [ ] Integração com APIs
- [ ] Testes unitários

### Fase 2: Funcionalidades Avançadas
- [ ] Gráficos interativos
- [ ] Notificações push
- [ ] Exportação de relatórios
- [ ] Integração com corretoras

### Fase 3: Otimizações
- [ ] Performance mobile
- [ ] Acessibilidade (WCAG)
- [ ] Testes A/B
- [ ] Personalização avançada

---

## 📄 Arquivos Gerados

1. **`wireframes_agente_investidor.pdf`** - Versão original com emojis
2. **`wireframes_agente_investidor_otimizado.pdf`** - Versão otimizada
3. **`wireframes_generator.py`** - Script gerador original
4. **`wireframes_optimized.py`** - Script gerador otimizado
5. **`WIREFRAMES_DOCUMENTATION.md`** - Esta documentação

---

## 🤝 Contribuições

Para sugestões ou melhorias nos wireframes:
1. Analise a documentação completa
2. Identifique pontos de melhoria
3. Proponha alterações baseadas em UX/UI
4. Considere impacto técnico e de negócio

---

## 📞 Contato

**Desenvolvedor:** Luiz Gustavo Finotello  
**Projeto:** Agente Investidor  
**Data:** Janeiro 2025  

---

*Esta documentação acompanha os wireframes do sistema Agente Investidor e deve ser utilizada como referência para o desenvolvimento da interface do usuário.*