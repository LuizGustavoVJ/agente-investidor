// Configuração da API
const API_BASE_URL = window.location.origin + '/api/agente';

// Estado da aplicação
let currentSection = 'home';

// Inicialização modular por página

document.addEventListener('DOMContentLoaded', function() {
    const path = window.location.pathname;
    if (path === '/' || path === '/index.html') {
        // Home/Análise/Chat
        try { initializeChatInput(); } catch(e){}
        try { populateStockSelect(); } catch(e){}
    }
    if (path === '/login') {
        setupLoginForm();
    }
    if (path === '/cadastro') {
        setupCadastroForm();
    }
});

function setupLoginForm() {
    const form = document.getElementById('login-form');
    if (!form) return;
    form.onsubmit = async function(e) {
            e.preventDefault();
        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value;
        const errorMsg = document.getElementById('login-error-msg');
        errorMsg.style.display = 'none';
        try {
            // Usar endpoint absoluto para login
            const resp = await fetch('/api/user/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await resp.json();
            console.log('Login response:', data);
            if (data.success && data.access_token) {
                setAuthToken(data.access_token);
                console.log('Token salvo:', getAuthToken());
                window.location.href = '/';
            } else {
                errorMsg.textContent = data.error || 'Erro ao fazer login.';
                errorMsg.style.display = 'block';
            }
        } catch (err) {
            errorMsg.textContent = 'Erro de conexão.';
            errorMsg.style.display = 'block';
        }
    };
}

function setupCadastroForm() {
    const form = document.getElementById('cadastro-form');
    if (!form) return;
    form.onsubmit = async function(e) {
        e.preventDefault();
        const username = document.getElementById('cadastro-username').value.trim();
        const email = document.getElementById('cadastro-email').value.trim();
        const password = document.getElementById('cadastro-password').value;
        const errorMsg = document.getElementById('cadastro-error-msg');
        const successMsg = document.getElementById('cadastro-success-msg');
        errorMsg.style.display = 'none';
        successMsg.style.display = 'none';
        try {
            const resp = await fetch(`${API_BASE_URL.replace('/agente','')}/user/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });
            const data = await resp.json();
            if (data.success) {
                successMsg.textContent = 'Cadastro realizado com sucesso! Faça login.';
                successMsg.style.display = 'block';
                errorMsg.style.display = 'none';
            } else {
                errorMsg.textContent = data.error || 'Erro ao cadastrar.';
                errorMsg.style.display = 'block';
                successMsg.style.display = 'none';
            }
        } catch (err) {
            errorMsg.textContent = 'Erro de conexão.';
            errorMsg.style.display = 'block';
            successMsg.style.display = 'none';
        }
    };
}

// Navegação
function showSection(sectionId) {
    console.log('showSection chamada para:', sectionId);
    // Esconder todas as seções
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => section.classList.remove('active'));
    // Mostrar seção selecionada
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
        currentSection = sectionId;
    } else {
        console.warn('Seção não encontrada:', sectionId);
    }
    // Atualizar navegação
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${sectionId}`) {
            link.classList.add('active');
        }
    });
    // Inicializar dashboard quando necessário
    if (sectionId === 'dashboard') {
        setTimeout(() => {
            try {
                initializeDashboard();
            } catch(e) {
                console.error('Erro ao inicializar dashboard:', e);
            }
        }, 100);
    }
}

// Análise de Ações
async function analyzeStock() {
    const symbol = document.getElementById('stock-select').value.trim().toUpperCase();
    const methodology = document.getElementById('methodology').value;
    
    if (!symbol) {
        alert('Por favor, selecione a ação');
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
        
        // Inicializar gráficos da análise
        setTimeout(() => {
            initializeStockAnalysisCharts(symbol);
        }, 500);
        
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

// Função para popular o select de ações
async function populateStockSelect() {
    const select = document.getElementById('stock-select');
    select.innerHTML = '<option value="">Carregando ações...</option>';
    try {
        const response = await fetch(`${API_BASE_URL}/acoes-disponiveis`);
        const data = await response.json();
        if (data.success && Array.isArray(data.acoes)) {
            select.innerHTML = '<option value="">Selecione...</option>';
            data.acoes.forEach(acao => {
                const opt = document.createElement('option');
                opt.value = acao.symbol;
                opt.textContent = `${acao.symbol} - ${acao.nome || ''} (${acao.bolsa || ''})`;
                select.appendChild(opt);
            });
        } else {
            select.innerHTML = '<option value="">Nenhuma ação disponível</option>';
        }
    } catch (e) {
        select.innerHTML = '<option value="">Erro ao carregar ações</option>';
    }
}

// --- Autenticação ---
const AUTH_TOKEN_KEY = 'access_token';

function getAuthToken() {
    return localStorage.getItem(AUTH_TOKEN_KEY);
}

function setAuthToken(token) {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
}

function clearAuthToken() {
    localStorage.removeItem(AUTH_TOKEN_KEY);
}

// Intercepta fetch para adicionar token
const originalFetch = window.fetch;
window.fetch = async (input, init = {}) => {
    const token = getAuthToken();
    if (token && typeof input === 'string' && (input.includes('/api/agente/') || input.includes('/api/user/'))) {
        init.headers = init.headers || {};
        init.headers['Authorization'] = 'Bearer ' + token;
    }
    return originalFetch(input, init);
};

// Lógica do modal
function setupAuthModal() {
    const form = document.getElementById('auth-form');
    form.onsubmit = async function(e) {
        e.preventDefault();
        const mode = document.getElementById('auth-modal-title').textContent === 'Entrar' ? 'login' : 'register';
        const username = document.getElementById('auth-username').value.trim();
        const email = document.getElementById('auth-email').value.trim();
        const password = document.getElementById('auth-password').value;
        const errorMsg = document.getElementById('auth-error-msg');
        errorMsg.style.display = 'none';
        try {
            if (mode === 'login') {
                const resp = await fetch(`${API_BASE_URL.replace('/agente','')}/user/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                const data = await resp.json();
                if (data.success && data.access_token) {
                    setAuthToken(data.access_token);
                    hideAuthModal();
                    location.reload();
                } else {
                    errorMsg.textContent = data.error || 'Erro ao fazer login.';
                    errorMsg.style.display = 'block';
                }
            } else {
                const resp = await fetch(`${API_BASE_URL.replace('/agente','')}/user/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, email, password })
                });
                const data = await resp.json();
                if (data.success) {
                    showAuthModal('login');
                } else {
                    errorMsg.textContent = data.error || 'Erro ao cadastrar.';
                    errorMsg.style.display = 'block';
                }
            }
        } catch (err) {
            errorMsg.textContent = 'Erro de conexão.';
            errorMsg.style.display = 'block';
        }
    };
}

// Checa autenticação ao carregar
function checkAuthOnLoad() {
    const token = getAuthToken();
    if (!token) {
        showAuthModal('login');
    } else {
        // Testa token
        fetch(`${API_BASE_URL.replace('/agente','')}/user/me`).then(r => r.json()).then(data => {
            if (!data.success) {
                clearAuthToken();
                showAuthModal('login');
            }
        }).catch(() => {
            clearAuthToken();
            showAuthModal('login');
        });
    }
}

function updateUserMenu() {
    const userMenu = document.getElementById('user-menu');
    const userInfo = document.getElementById('user-info');
    const userDropdown = document.getElementById('user-dropdown');
    const menuLogin = document.getElementById('menu-login');
    const menuCadastro = document.getElementById('menu-cadastro');
    if (!userMenu || !userInfo || !userDropdown || !menuLogin || !menuCadastro) {
        return;
    }
    const token = getAuthToken();
    if (token) {
        fetch(`${API_BASE_URL.replace('/agente','')}/user/me`).then(async r => {
            let data;
            try {
                data = await r.json();
            } catch (e) {
                clearAuthToken();
                userMenu.style.display = 'none';
                menuLogin.style.display = 'inline-block';
                menuCadastro.style.display = 'inline-block';
                return;
            }
            if (data.success) {
                userInfo.textContent = data.user.username;
                userMenu.style.display = 'inline-block';
                menuLogin.style.display = 'none';
                menuCadastro.style.display = 'none';
            } else {
                clearAuthToken();
                userMenu.style.display = 'none';
                menuLogin.style.display = 'inline-block';
                menuCadastro.style.display = 'inline-block';
            }
        });
    } else {
        userMenu.style.display = 'none';
        menuLogin.style.display = 'inline-block';
        menuCadastro.style.display = 'inline-block';
    }
    // Dropdown toggle
    userInfo.onclick = function(e) {
        e.preventDefault();
        userDropdown.style.display = userDropdown.style.display === 'block' ? 'none' : 'block';
    };
    // Fechar dropdown ao clicar fora
    document.addEventListener('click', function(e) {
        if (!userMenu.contains(e.target)) {
            userDropdown.style.display = 'none';
        }
    });
    // Logout
    document.getElementById('menu-logout').onclick = function(e) {
        e.preventDefault();
        clearAuthToken();
        window.location.href = '/';
    };
}

document.addEventListener('DOMContentLoaded', function() {
    updateUserMenu();
    // ... restante da inicialização modular ...
});



// ===== DASHBOARD FUNCTIONALITY =====

// Variáveis globais para os gráficos
let ibovespaChart = null;
let sectorChart = null;
let topStocksChart = null;
let volatilityChart = null;
let stockPriceChart = null;
let stockVolumeChart = null;
let technicalChart = null;
let comparisonChart = null;
let fundamentalsChart = null;
let miniCharts = {};

// Inicializar Dashboard
function initializeDashboard() {
    loadMarketSummary();
    initializeCharts();
    loadFeaturedStocks();
    loadEconomicIndicators();
}

// Carregar resumo do mercado
async function loadMarketSummary() {
    try {
        // Simular dados do mercado (em produção, viria de APIs reais)
        const marketData = {
            ibovespa: { value: 126543, change: 1.25 },
            dolar: { value: 5.18, change: -0.45 },
            selic: { value: 11.75 },
            volume: { value: 18.5 }
        };

        // Atualizar valores na interface
        document.getElementById('ibovespa-value').textContent = marketData.ibovespa.value.toLocaleString('pt-BR');
        document.getElementById('ibovespa-change').textContent = `${marketData.ibovespa.change > 0 ? '+' : ''}${marketData.ibovespa.change}%`;
        document.getElementById('ibovespa-change').className = `change-indicator ${marketData.ibovespa.change > 0 ? 'positive' : 'negative'}`;

        document.getElementById('dolar-value').textContent = `R$ ${marketData.dolar.value.toFixed(2)}`;
        document.getElementById('dolar-change').textContent = `${marketData.dolar.change > 0 ? '+' : ''}${marketData.dolar.change}%`;
        document.getElementById('dolar-change').className = `change-indicator ${marketData.dolar.change > 0 ? 'positive' : 'negative'}`;

        document.getElementById('selic-value').textContent = `${marketData.selic.value}%`;
        document.getElementById('volume-value').textContent = `R$ ${marketData.volume.value}`;

    } catch (error) {
        console.error('Erro ao carregar resumo do mercado:', error);
    }
}

// Inicializar todos os gráficos
function initializeCharts() {
    initializeIbovespaChart();
    initializeSectorChart();
    initializeTopStocksChart();
    initializeVolatilityChart();
    initializeEconomicCharts();
}

function initializeEconomicCharts() {
    // Inicialização simulada dos gráficos econômicos
    // Exemplo: mini-charts de IPCA, PIB, Desemprego, Commodities
    const charts = [
        { id: 'ipcaChart', label: 'IPCA', data: [3.5, 4.2, 5.1, 4.8, 3.9] },
        { id: 'pibChart', label: 'PIB', data: [1.2, 1.5, 2.1, 1.8, 2.3] },
        { id: 'unemploymentChart', label: 'Desemprego', data: [12, 11.5, 10.8, 9.9, 9.2] },
        { id: 'commoditiesChart', label: 'Commodities', data: [100, 110, 120, 115, 130] }
    ];
    charts.forEach(chart => {
        const ctx = document.getElementById(chart.id);
        if (!ctx) return;
        if (miniCharts[chart.id]) {
            miniCharts[chart.id].destroy();
        }
        miniCharts[chart.id] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['2019', '2020', '2021', '2022', '2023'],
                datasets: [{
                    label: chart.label,
                    data: chart.data,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: false } }
            }
        });
    });
}

// Gráfico do Ibovespa
function initializeIbovespaChart() {
    const ctx = document.getElementById('ibovespaChart');
    if (!ctx) return;

    // Destruir gráfico existente se houver
    if (ibovespaChart) {
        ibovespaChart.destroy();
        ibovespaChart = null;
    }

    // Dados simulados do Ibovespa (últimos 30 dias)
    const labels = [];
    const data = [];
    const baseValue = 126000;
    
    for (let i = 29; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }));
        
        // Simular variação do índice
        const variation = (Math.random() - 0.5) * 2000;
        data.push(baseValue + variation + (Math.random() * 3000));
    }

    ibovespaChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Ibovespa',
                data: data,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString('pt-BR');
                        }
                    }
                }
            }
        }
    });
}

// Gráfico de Setores
function initializeSectorChart() {
    const ctx = document.getElementById('sectorChart');
    if (!ctx) return;

    // Destruir gráfico existente se houver
    if (sectorChart) {
        sectorChart.destroy();
        sectorChart = null;
    }

    const sectors = ['Financeiro', 'Petróleo', 'Mineração', 'Varejo', 'Tecnologia'];
    const performance = [2.1, 1.8, 3.2, 0.9, 4.1];

    sectorChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sectors,
            datasets: [{
                label: 'Performance (%)',
                data: performance,
                backgroundColor: performance.map(val => val > 0 ? '#16a34a' : '#dc2626'),
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

// Gráfico Top Ações
function initializeTopStocksChart() {
    const ctx = document.getElementById('topStocksChart');
    if (!ctx) return;

    // Destruir gráfico existente se houver
    if (topStocksChart) {
        topStocksChart.destroy();
        topStocksChart = null;
    }

    const stocks = ['PETR4', 'VALE3', 'ITUB4', 'BBDC4', 'ABEV3'];
    const gains = [5.2, 3.8, 2.1, 4.5, 1.9];

    topStocksChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: stocks,
            datasets: [{
                label: 'Variação (%)',
                data: gains,
                backgroundColor: '#16a34a',
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y', // Isso faz o gráfico ser horizontal
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

// Gráfico de Volatilidade
function initializeVolatilityChart() {
    const ctx = document.getElementById('volatilityChart');
    if (!ctx) return;

    // Destruir gráfico existente se houver
    if (volatilityChart) {
        volatilityChart.destroy();
        volatilityChart = null;
    }

    const labels = [];
    const volatilityData = [];
    
    for (let i = 19; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }));
        volatilityData.push(Math.random() * 3 + 1); // Volatilidade entre 1% e 4%
    }

    volatilityChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Volatilidade (%)',
                data: volatilityData,
                borderColor: '#f59e0b',
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(1) + '%';
                        }
                    }
                }
            }
        }
    });
}

// Carregar ações em destaque
async function loadFeaturedStocks() {
    try {
        // Dados simulados de ações em destaque
        const featuredStocks = [
            { symbol: 'PETR4', name: 'Petrobras', price: 31.45, change: 2.1, volume: '125M', pe: 8.5, divYield: 12.5, score: 85 },
            { symbol: 'VALE3', name: 'Vale', price: 68.20, change: 1.8, volume: '89M', pe: 6.2, divYield: 8.9, score: 78 },
            { symbol: 'ITUB4', name: 'Itaú Unibanco', price: 25.80, change: -0.5, volume: '156M', pe: 9.1, divYield: 6.2, score: 72 },
            { symbol: 'BBDC4', name: 'Bradesco', price: 13.45, change: 1.2, volume: '98M', pe: 7.8, divYield: 7.1, score: 69 },
            { symbol: 'ABEV3', name: 'Ambev', price: 12.90, change: 0.8, volume: '67M', pe: 15.2, divYield: 4.5, score: 65 }
        ];

        const tbody = document.getElementById('featuredStocksBody');
        if (!tbody) return;

        tbody.innerHTML = featuredStocks.map(stock => `
            <tr>
                <td>
                    <div class="stock-symbol">${stock.symbol}</div>
                    <div class="stock-name">${stock.name}</div>
                </td>
                <td>R$ ${stock.price.toFixed(2)}</td>
                <td class="price-change ${stock.change > 0 ? 'positive' : 'negative'}">
                    ${stock.change > 0 ? '+' : ''}${stock.change}%
                </td>
                <td>${stock.volume}</td>
                <td>${stock.pe}</td>
                <td>${stock.divYield}%</td>
                <td>
                    <span class="score-badge ${getScoreBadgeClass(stock.score)}">
                        ${stock.score}
                    </span>
                </td>
                <td>
                    <button class="action-btn analyze" onclick="analyzeStockFromTable('${stock.symbol}')">
                        Analisar
                    </button>
                </td>
            </tr>
        `).join('');

    } catch (error) {
        console.error('Erro ao carregar ações em destaque:', error);
    }
}

// Função auxiliar para classe do score
function getScoreBadgeClass(score) {
    if (score >= 80) return 'excellent';
    if (score >= 70) return 'good';
    if (score >= 60) return 'average';
    return 'poor';
}

// Analisar ação da tabela
function analyzeStockFromTable(symbol) {
    document.getElementById('stock-symbol').value = symbol;
    showSection('analise');
    analyzeStock();
}

// Carregar indicadores econômicos
async function loadEconomicIndicators() {
    try {
        // Dados simulados de indicadores econômicos
        const indicators = {
            ipca: { value: '4.62%', data: [4.1, 4.3, 4.5, 4.6, 4.62] },
            pib: { value: '2.1%', data: [1.8, 1.9, 2.0, 2.05, 2.1] },
            unemployment: { value: '8.9%', data: [9.5, 9.2, 9.0, 8.95, 8.9] },
            commodities: { value: '+2.3%', data: [98, 101, 99, 102, 103] }
        };

        // Atualizar valores
        document.getElementById('ipca-value').textContent = indicators.ipca.value;
        document.getElementById('pib-value').textContent = indicators.pib.value;
        document.getElementById('unemployment-value').textContent = indicators.unemployment.value;
        document.getElementById('commodities-value').textContent = indicators.commodities.value;

        // Criar mini gráficos
        createMiniChart('ipcaChart', indicators.ipca.data, '#f59e0b');
        createMiniChart('pibChart', indicators.pib.data, '#16a34a');
        createMiniChart('unemploymentChart', indicators.unemployment.data, '#dc2626');
        createMiniChart('commoditiesChart', indicators.commodities.data, '#8b5cf6');

    } catch (error) {
        console.error('Erro ao carregar indicadores econômicos:', error);
    }
}

// Criar mini gráfico
function createMiniChart(canvasId, data, color) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    if (miniCharts[canvasId]) {
        try {
            miniCharts[canvasId].destroy();
        } catch (e) {
            console.warn('Erro ao destruir miniChart:', canvasId, e);
        }
    }
    miniCharts[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['2019', '2020', '2021', '2022', '2023'],
            datasets: [{
                label: '',
                data: data,
                borderColor: color,
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: false } }
        }
    });
}

// Funções de atualização dos gráficos
function updateIbovespaChart(period) {
    // Atualizar botões ativos
    document.querySelectorAll('#ibovespaChart').forEach(chart => {
        chart.parentElement.querySelectorAll('.chart-btn').forEach(btn => {
            btn.classList.remove('active');
        });
    });
    event.target.classList.add('active');

    // Simular novos dados baseados no período
    const dataPoints = period === '1M' ? 30 : period === '3M' ? 90 : period === '6M' ? 180 : 365;
    const newLabels = [];
    const newData = [];
    
    for (let i = dataPoints - 1; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        newLabels.push(date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }));
        newData.push(126000 + (Math.random() - 0.5) * 5000);
    }

    ibovespaChart.data.labels = newLabels;
    ibovespaChart.data.datasets[0].data = newData;
    ibovespaChart.update();
}

function updateSectorChart(type) {
    // Atualizar botões ativos
    event.target.parentElement.querySelectorAll('.chart-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    const sectors = ['Bancos', 'Petróleo', 'Mineração', 'Varejo', 'Tecnologia', 'Energia'];
    let newData;

    if (type === 'performance') {
        newData = [2.5, 1.8, -0.5, 3.2, 4.1, 1.2];
        sectorChart.data.datasets[0].label = 'Performance (%)';
    } else {
        newData = [15.2, 12.8, 8.5, 18.2, 22.1, 9.2];
        sectorChart.data.datasets[0].label = 'Volume (bilhões)';
    }

    sectorChart.data.datasets[0].data = newData;
    sectorChart.data.datasets[0].backgroundColor = newData.map(val => 
        type === 'performance' ? (val > 0 ? '#16a34a' : '#dc2626') : '#667eea'
    );
    sectorChart.update();
}

function updateTopStocks(type) {
    // Atualizar botões ativos
    event.target.parentElement.querySelectorAll('.chart-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    const stocks = ['PETR4', 'VALE3', 'ITUB4', 'BBDC4', 'ABEV3'];
    let newData, label, color;

    switch(type) {
        case 'gainers':
            newData = [5.2, 3.8, 2.1, 4.5, 1.9];
            label = 'Maiores Altas (%)';
            color = '#16a34a';
            break;
        case 'losers':
            newData = [-2.1, -1.5, -3.2, -0.8, -2.9];
            label = 'Maiores Baixas (%)';
            color = '#dc2626';
            break;
        case 'volume':
            newData = [125, 89, 156, 98, 67];
            label = 'Volume (milhões)';
            color = '#667eea';
            break;
    }

    topStocksChart.data.datasets[0].data = newData;
    topStocksChart.data.datasets[0].label = label;
    topStocksChart.data.datasets[0].backgroundColor = color;
    topStocksChart.update();
}

function updateVolatilityChart(period) {
    // Atualizar botões ativos
    event.target.parentElement.querySelectorAll('.chart-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    const dataPoints = period === 'daily' ? 20 : 12;
    const newLabels = [];
    const newData = [];
    
    for (let i = dataPoints - 1; i >= 0; i--) {
        const date = new Date();
        if (period === 'daily') {
            date.setDate(date.getDate() - i);
            newLabels.push(date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }));
        } else {
            date.setDate(date.getDate() - (i * 7));
            newLabels.push(`Sem ${Math.ceil((dataPoints - i))}`)
        }
        newData.push(Math.random() * 3 + 1);
    }

    volatilityChart.data.labels = newLabels;
    volatilityChart.data.datasets[0].data = newData;
    volatilityChart.update();
}

function updateFeaturedStocks(category) {
    // Atualizar botões ativos
    event.target.parentElement.querySelectorAll('.table-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    // Recarregar dados baseado na categoria
    loadFeaturedStocks();
}

// Inicializar gráficos da análise de ações
function initializeStockAnalysisCharts(symbol) {
    document.getElementById('chart-stock-symbol').textContent = symbol;
    document.getElementById('stock-charts').style.display = 'block';
    
    initializeStockPriceChart(symbol);
    initializeStockVolumeChart(symbol);
    initializeTechnicalChart(symbol);
    initializeComparisonChart(symbol);
    initializeFundamentalsChart(symbol);
    loadDetailedMetrics(symbol);
}

function initializeStockPriceChart(symbol) {
    const ctx = document.getElementById('stockPriceChart');
    if (!ctx) return;

    // Dados simulados de preço
    const labels = [];
    const prices = [];
    const basePrice = 30;
    
    for (let i = 29; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }));
        prices.push(basePrice + (Math.random() - 0.5) * 5);
    }

    if (stockPriceChart) {
        stockPriceChart.destroy();
    }

    stockPriceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: `${symbol} - Preço`,
                data: prices,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return 'R$ ' + value.toFixed(2);
                        }
                    }
                }
            }
        }
    });
}

function initializeStockVolumeChart(symbol) {
    const ctx = document.getElementById('stockVolumeChart');
    if (!ctx) return;

    // Dados simulados de volume
    const labels = [];
    const volumes = [];
    
    for (let i = 29; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }));
        volumes.push(Math.random() * 50000000 + 10000000);
    }

    if (stockVolumeChart) {
        stockVolumeChart.destroy();
    }

    stockVolumeChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Volume',
                data: volumes,
                backgroundColor: '#f59e0b',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return (value / 1000000).toFixed(1) + 'M';
                        }
                    }
                }
            }
        }
    });
}

function initializeTechnicalChart(symbol) {
    const ctx = document.getElementById('technicalChart');
    if (!ctx) return;

    // Dados simulados de RSI
    const labels = [];
    const rsiData = [];
    
    for (let i = 19; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }));
        rsiData.push(Math.random() * 40 + 30); // RSI entre 30 e 70
    }

    if (technicalChart) {
        technicalChart.destroy();
    }

    technicalChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'RSI',
                data: rsiData,
                borderColor: '#8b5cf6',
                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(0);
                        }
                    }
                }
            }
        }
    });
}

function initializeComparisonChart(symbol) {
    const ctx = document.getElementById('comparisonChart');
    if (!ctx) return;

    // Dados simulados de comparação
    const labels = [];
    const stockData = [];
    const ibovespaData = [];
    
    for (let i = 29; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }));
        stockData.push((Math.random() - 0.5) * 10);
        ibovespaData.push((Math.random() - 0.5) * 5);
    }

    if (comparisonChart) {
        comparisonChart.destroy();
    }

    comparisonChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: symbol,
                data: stockData,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 2,
                fill: false,
                tension: 0.4
            }, {
                label: 'Ibovespa',
                data: ibovespaData,
                borderColor: '#16a34a',
                backgroundColor: 'rgba(22, 163, 74, 0.1)',
                borderWidth: 2,
                fill: false,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: true }
            },
            scales: {
                y: {
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(1) + '%';
                        }
                    }
                }
            }
        }
    });
}

function initializeFundamentalsChart(symbol) {
    const ctx = document.getElementById('fundamentalsChart');
    if (!ctx) return;

    const metrics = ['P/E', 'P/B', 'ROE', 'ROA', 'Margem'];
    const values = [12.5, 1.8, 15.2, 8.5, 12.8];

    if (fundamentalsChart) {
        fundamentalsChart.destroy();
    }

    fundamentalsChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: metrics,
            datasets: [{
                label: symbol,
                data: values,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.2)',
                borderWidth: 2,
                pointBackgroundColor: '#667eea'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 20
                }
            }
        }
    });
}

function loadDetailedMetrics(symbol) {
    // Dados simulados de métricas detalhadas
    const metrics = {
        pe: '12.5',
        pb: '1.8',
        peg: '1.2',
        evEbitda: '8.5',
        roe: '15.2%',
        roa: '8.5%',
        roic: '12.8%',
        margin: '12.8%',
        debtEquity: '0.45',
        currentRatio: '1.8',
        netDebtEbitda: '2.1',
        revenueGrowth: '8.5%',
        earningsGrowth: '12.3%',
        dividendYield: '6.2%'
    };

    // Atualizar valores na interface
    Object.keys(metrics).forEach(key => {
        const element = document.getElementById(`metric-${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`);
        if (element) {
            element.textContent = metrics[key];
        }
    });
}

// Funções de atualização dos gráficos de análise
function updateStockChart(period) {
    // Atualizar botões ativos
    event.target.parentElement.querySelectorAll('.chart-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    // Recriar gráfico com novo período
    const symbol = document.getElementById('chart-stock-symbol').textContent;
    initializeStockPriceChart(symbol);
}

function updateTechnicalChart(indicator) {
    // Atualizar botões ativos
    event.target.parentElement.querySelectorAll('.chart-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    // Simular dados do indicador selecionado
    const symbol = document.getElementById('chart-stock-symbol').textContent;
    initializeTechnicalChart(symbol);
}

function updateComparisonChart(comparison) {
    // Atualizar botões ativos
    event.target.parentElement.querySelectorAll('.chart-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    // Recriar gráfico com nova comparação
    const symbol = document.getElementById('chart-stock-symbol').textContent;
    initializeComparisonChart(symbol);
}

window.showSection = showSection;

