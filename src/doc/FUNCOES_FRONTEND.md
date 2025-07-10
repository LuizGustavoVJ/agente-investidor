# Documentação Técnica das Funções Frontend (script.js)

## Navegação SPA
- **showSection(sectionId):** Exibe a seção correspondente, esconde as demais, atualiza menu e inicializa dashboard se necessário.
- **window.showSection:** Exporta showSection para uso global (onclick no HTML).

## Autenticação
- **getAuthToken():** Retorna o JWT salvo no localStorage.
- **setAuthToken(token):** Salva o JWT no localStorage.
- **clearAuthToken():** Remove o JWT do localStorage.
- **updateUserMenu():** Atualiza o menu do usuário logado/deslogado.
- **checkAuthOnLoad():** Verifica autenticação ao carregar a página.

## Integração com API
- **fetchStockData(symbol):** Busca dados de uma ação via API.
- **analyzeWithMethodology(symbol, methodology, stockData):** Envia dados para análise fundamentalista.
- **sendChatMessage():** Envia mensagem para o chat do agente.
- **sendMessage(message):** Envia mensagem rápida para o chat.

## Dashboard e Gráficos
- **initializeDashboard():** Inicializa/reseta o dashboard de mercado.
- **updateIbovespaChart(period):** Atualiza gráfico do Ibovespa.
- **updateSectorChart(type):** Atualiza gráfico de setores.
- **updateTopStocks(type):** Atualiza gráfico de top ações.
- **updateVolatilityChart(period):** Atualiza gráfico de volatilidade.
- **updateFeaturedStocks(category):** Atualiza tabela de ações em destaque.
- **initializeStockAnalysisCharts(symbol):** Inicializa gráficos da análise de ação.
- **updateStockChart(period):** Atualiza gráfico de preço da ação.
- **updateTechnicalChart(indicator):** Atualiza gráfico técnico.
- **updateComparisonChart(comparison):** Atualiza gráfico de comparação.

## Análise de Ações
- **analyzeStock():** Coleta dados do formulário, chama API e exibe resultados.
- **displayAnalysisResults(data):** Atualiza a interface com os resultados da análise.
- **showLoading(show):** Exibe/esconde loading da análise.
- **hideResults():** Esconde resultados da análise.

## Chat
- **initializeChatInput():** Inicializa input do chat.
- **addMessageToChat(message, sender):** Adiciona mensagem ao chat.
- **formatMessage(message):** Formata mensagem para exibição.

## Utilitários
- **showNotification(message, type):** Exibe notificação na interface.
- **populateStockSelect():** Preenche select de ações.
- **validateStockSymbol(symbol):** Valida símbolo de ação.
- **formatCurrency(value):** Formata valor monetário.
- **formatPercentage(value):** Formata valor percentual.

## Observações
- Todas as funções principais possuem comentários explicativos no código.
- Funções usadas em onclick devem ser exportadas via window para funcionar no HTML.
- A navegação SPA depende da correta ativação das seções e do menu. 