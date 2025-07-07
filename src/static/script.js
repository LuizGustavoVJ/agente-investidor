// Configuração da API
const API_BASE_URL = window.location.origin + '/api/agente';

// Estado da aplicação
let currentSection = 'home';

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    initializeChatInput();
    showSection('home');
});

// Navegação
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const sectionId = this.getAttribute('href').substring(1);
            showSection(sectionId);
            
            // Atualizar estado ativo
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

function showSection(sectionId) {
    // Esconder todas as seções
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => section.classList.remove('active'));
    
    // Mostrar seção selecionada
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
        currentSection = sectionId;
    }
    
    // Atualizar navegação
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${sectionId}`) {
            link.classList.add('active');
        }
    });
}

// Análise de Ações
async function analyzeStock() {
    const symbol = document.getElementById('stock-symbol').value.trim().toUpperCase();
    const methodology = document.getElementById('methodology').value;
    
    if (!symbol) {
        alert('Por favor, digite o símbolo da ação');
        return;
    }
    
    // Mostrar loading
    showLoading(true);
    hideResults();
    
    try {
        // Primeiro, obter dados da ação
        const stockData = await fetchStockData(symbol);
        
        // Depois, analisar com a metodologia selecionada
        const analysisData = await analyzeWithMethodology(symbol, methodology, stockData);
        
        // Mostrar resultados
        displayAnalysisResults(analysisData);
        
    } catch (error) {
        console.error('Erro na análise:', error);
        alert('Erro ao analisar a ação. Verifique o símbolo e tente novamente.');
    } finally {
        showLoading(false);
    }
}

async function fetchStockData(symbol) {
    const response = await fetch(`${API_BASE_URL}/dados-acao/${symbol}`);
    
    if (!response.ok) {
        throw new Error(`Erro ao obter dados da ação: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (!data.success) {
        throw new Error(data.error || 'Erro desconhecido');
    }
    
    return data.data;
}

async function analyzeWithMethodology(symbol, methodology, stockData) {
    // Extrair dados financeiros básicos dos dados da ação
    let financialData = {
        symbol: symbol,
        metodologia: methodology
    };
    
    // Tentar extrair dados do chart se disponível
    if (stockData.chart && stockData.chart.chart && stockData.chart.chart.result) {
        const result = stockData.chart.chart.result[0];
        const meta = result.meta;
        
        financialData.price = meta.regularMarketPrice;
        financialData.market_cap = meta.marketCap;
        
        // Para demonstração, vamos usar alguns valores fictícios baseados no preço
        // Em uma implementação real, estes dados viriam de APIs especializadas
        const price = meta.regularMarketPrice || 50;
        financialData.pe_ratio = 12 + Math.random() * 8; // 12-20
        financialData.pb_ratio = 1 + Math.random() * 1.5; // 1-2.5
        financialData.peg_ratio = 0.5 + Math.random() * 1; // 0.5-1.5
        financialData.dividend_yield = 2 + Math.random() * 6; // 2-8%
        financialData.roe = 10 + Math.random() * 15; // 10-25%
        financialData.roa = 5 + Math.random() * 10; // 5-15%
        financialData.debt_to_equity = Math.random() * 0.8; // 0-0.8
        financialData.current_ratio = 1.2 + Math.random() * 1.3; // 1.2-2.5
        financialData.free_cash_flow = 100000000 + Math.random() * 500000000;
        financialData.revenue_growth = 5 + Math.random() * 20; // 5-25%
        financialData.earnings_growth = 5 + Math.random() * 25; // 5-30%
        financialData.profit_margin = 5 + Math.random() * 15; // 5-20%
        financialData.operating_margin = 8 + Math.random() * 12; // 8-20%
        financialData.book_value_per_share = price * (0.7 + Math.random() * 0.6); // 70-130% do preço
        financialData.earnings_per_share = price / (12 + Math.random() * 8); // P/E entre 12-20
    }
    
    const response = await fetch(`${API_BASE_URL}/analisar-acao`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(financialData)
    });
    
    if (!response.ok) {
        throw new Error(`Erro na análise: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (!data.success) {
        throw new Error(data.error || 'Erro na análise');
    }
    
    return data.data;
}

function displayAnalysisResults(data) {
    // Atualizar elementos da interface
    document.getElementById('result-symbol').textContent = data.symbol;
    document.getElementById('result-score-value').textContent = Math.round(data.score);
    
    // Recomendação
    const recommendationElement = document.getElementById('result-recommendation');
    recommendationElement.textContent = data.recomendacao;
    recommendationElement.className = `recommendation-badge ${data.recomendacao.toLowerCase()}`;
    
    // Pontos fortes
    const strengthsList = document.getElementById('result-strengths');
    strengthsList.innerHTML = '';
    data.pontos_fortes.forEach(point => {
        const li = document.createElement('li');
        li.textContent = point;
        strengthsList.appendChild(li);
    });
    
    // Pontos fracos
    const weaknessesList = document.getElementById('result-weaknesses');
    weaknessesList.innerHTML = '';
    data.pontos_fracos.forEach(point => {
        const li = document.createElement('li');
        li.textContent = point;
        weaknessesList.appendChild(li);
    });
    
    // Informações adicionais
    document.getElementById('result-methodology').textContent = data.metodologia_aplicada;
    document.getElementById('result-current-price').textContent = data.preco_atual ? data.preco_atual.toFixed(2) : 'N/A';
    
    // Preço alvo (se disponível)
    const targetPriceElement = document.getElementById('result-target-price');
    if (data.preco_alvo) {
        document.getElementById('target-price-value').textContent = data.preco_alvo.toFixed(2);
        targetPriceElement.style.display = 'inline';
    } else {
        targetPriceElement.style.display = 'none';
    }
    
    // Justificativa
    document.getElementById('result-justification').textContent = data.justificativa;
    
    // Mostrar resultados
    document.getElementById('analysis-results').style.display = 'block';
}

function showLoading(show) {
    const loadingElement = document.getElementById('analysis-loading');
    loadingElement.style.display = show ? 'block' : 'none';
}

function hideResults() {
    document.getElementById('analysis-results').style.display = 'none';
}

// Chat
function initializeChatInput() {
    const chatInput = document.getElementById('chat-input');
    
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });
}

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Adicionar mensagem do usuário
    addMessageToChat(message, 'user');
    
    // Limpar input
    input.value = '';
    
    try {
        // Enviar para API
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                mensagem: message,
                contexto: {}
            })
        });
        
        if (!response.ok) {
            throw new Error(`Erro no chat: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            // Adicionar resposta do agente
            addMessageToChat(data.data.resposta, 'agent');
        } else {
            throw new Error(data.error || 'Erro desconhecido');
        }
        
    } catch (error) {
        console.error('Erro no chat:', error);
        addMessageToChat('Desculpe, ocorreu um erro. Tente novamente.', 'agent');
    }
}

function sendMessage(message) {
    document.getElementById('chat-input').value = message;
    sendChatMessage();
}

function addMessageToChat(message, sender) {
    const chatMessages = document.getElementById('chat-messages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = sender === 'agent' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    // Processar quebras de linha e formatação
    const formattedMessage = formatMessage(message);
    content.innerHTML = formattedMessage;
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll para baixo
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatMessage(message) {
    // Converter quebras de linha
    let formatted = message.replace(/\n/g, '<br>');
    
    // Converter markdown básico
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Converter listas
    formatted = formatted.replace(/^• (.+)$/gm, '<li>$1</li>');
    formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    
    // Converter emojis de texto
    formatted = formatted.replace(/:\)/g, '😊');
    formatted = formatted.replace(/:\(/g, '😞');
    
    return formatted;
}

// Utilitários
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

function formatPercentage(value) {
    return `${value.toFixed(2)}%`;
}

// Animações e efeitos
function addScrollEffects() {
    const cards = document.querySelectorAll('.stat-card, .investor-card, .methodology-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    });
    
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.6s ease';
        observer.observe(card);
    });
}

// Inicializar efeitos quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(addScrollEffects, 500);
});

// Função para demonstração - simular dados de mercado
async function loadMarketData() {
    try {
        const response = await fetch(`${API_BASE_URL}/recomendacoes-mercado`);
        
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                console.log('Dados do mercado:', data.data);
                // Aqui você pode atualizar a interface com dados reais do mercado
            }
        }
    } catch (error) {
        console.log('Dados do mercado não disponíveis:', error);
    }
}

// Carregar dados do mercado na inicialização
document.addEventListener('DOMContentLoaded', function() {
    loadMarketData();
});

// Função para validar símbolos de ações
function validateStockSymbol(symbol) {
    // Padrões básicos para símbolos
    const patterns = {
        brazilian: /^[A-Z]{4}[0-9]{1,2}\.SA$/,  // PETR4.SA
        us: /^[A-Z]{1,5}$/,                      // AAPL
        general: /^[A-Z0-9]{1,10}(\.[A-Z]{1,3})?$/ // Geral
    };
    
    return patterns.brazilian.test(symbol) || 
           patterns.us.test(symbol) || 
           patterns.general.test(symbol);
}

// Adicionar validação ao input de símbolo
document.addEventListener('DOMContentLoaded', function() {
    const symbolInput = document.getElementById('stock-symbol');
    
    if (symbolInput) {
        symbolInput.addEventListener('input', function() {
            const symbol = this.value.toUpperCase();
            this.value = symbol;
            
            // Feedback visual básico
            if (symbol.length > 0 && !validateStockSymbol(symbol)) {
                this.style.borderColor = '#ef4444';
            } else {
                this.style.borderColor = '';
            }
        });
    }
});

// Função para mostrar notificações
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#667eea'};
        color: white;
        padding: 1rem 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Adicionar estilos para animações de notificação
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

