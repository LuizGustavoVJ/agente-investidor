"""
Serviço de Análises Financeiras Avançadas - Agente Investidor
Implementa 50+ indicadores financeiros e análises de risco

Autor: Luiz Gustavo Finotello
Data: 10 de Julho de 2025
"""

import asyncio
import json
import logging
import math
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import aiohttp
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST
from starlette.responses import Response
import uvicorn

# Imports locais
from shared.models.dto import (
    StockData, AnalysisRequest, AnalysisResponse, 
    FinancialRatios, ValuationMetrics, RiskMetrics
)
from shared.cache.advanced_cache import AdvancedCache
from shared.messaging.kafka_client import KafkaClient

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Métricas Prometheus
analysis_requests = Counter('analysis_requests_total', 'Total analysis requests', ['analysis_type'])
analysis_duration = Histogram('analysis_duration_seconds', 'Analysis processing time', ['analysis_type'])
analysis_errors = Counter('analysis_errors_total', 'Analysis errors', ['error_type'])
active_analyses = Gauge('active_analyses', 'Currently active analyses')
cache_hit_ratio = Gauge('analysis_cache_hit_ratio', 'Cache hit ratio for analyses')

# FastAPI app
app = FastAPI(
    title="Analysis Service",
    description="Serviço de Análises Financeiras Avançadas",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Global instances
cache: Optional[AdvancedCache] = None
kafka_client: Optional[KafkaClient] = None
redis_client: Optional[redis.Redis] = None

class AnalysisType(str):
    FUNDAMENTAL = "fundamental"
    TECHNICAL = "technical"
    COMPREHENSIVE = "comprehensive"
    RISK = "risk"
    VALUATION = "valuation"
    SECTOR = "sector"
    COMPARATIVE = "comparative"

class AdvancedAnalysisRequest(BaseModel):
    stock_symbol: str = Field(..., description="Símbolo da ação")
    analysis_type: str = Field(default=AnalysisType.COMPREHENSIVE, description="Tipo de análise")
    include_ratios: bool = Field(default=True, description="Incluir indicadores financeiros")
    include_valuation: bool = Field(default=True, description="Incluir métricas de valuation")
    include_risk: bool = Field(default=True, description="Incluir análise de risco")
    include_technical: bool = Field(default=False, description="Incluir análise técnica")
    benchmark_symbols: Optional[List[str]] = Field(default=None, description="Símbolos para comparação")
    time_period: int = Field(default=252, description="Período em dias para análise")
    confidence_level: float = Field(default=0.95, description="Nível de confiança para VaR")

class AdvancedAnalysisResponse(BaseModel):
    stock_symbol: str
    analysis_type: str
    timestamp: datetime
    financial_ratios: Optional[Dict[str, float]] = None
    valuation_metrics: Optional[Dict[str, float]] = None
    risk_metrics: Optional[Dict[str, float]] = None
    technical_indicators: Optional[Dict[str, float]] = None
    sector_analysis: Optional[Dict[str, Any]] = None
    comparative_analysis: Optional[Dict[str, Any]] = None
    recommendation: str
    score: float
    confidence: float
    summary: str

class FinancialAnalyzer:
    """Analisador financeiro avançado com 50+ indicadores"""
    
    def __init__(self):
        self.risk_free_rate = 0.045  # Taxa Selic aproximada
        
    async def analyze_stock(self, request: AdvancedAnalysisRequest) -> AdvancedAnalysisResponse:
        """Executa análise completa da ação"""
        logger.info(f"Starting analysis for {request.stock_symbol}")
        
        # Busca dados da ação
        stock_data = await self._get_stock_data(request.stock_symbol)
        historical_data = await self._get_historical_data(request.stock_symbol, request.time_period)
        
        response = AdvancedAnalysisResponse(
            stock_symbol=request.stock_symbol,
            analysis_type=request.analysis_type,
            timestamp=datetime.now(),
            recommendation="HOLD",
            score=0.0,
            confidence=0.0,
            summary=""
        )
        
        # Análises específicas
        if request.include_ratios:
            response.financial_ratios = await self._calculate_financial_ratios(stock_data, historical_data)
        
        if request.include_valuation:
            response.valuation_metrics = await self._calculate_valuation_metrics(stock_data, historical_data)
        
        if request.include_risk:
            response.risk_metrics = await self._calculate_risk_metrics(stock_data, historical_data, request.confidence_level)
        
        if request.include_technical:
            response.technical_indicators = await self._calculate_technical_indicators(historical_data)
        
        if request.analysis_type == AnalysisType.SECTOR:
            response.sector_analysis = await self._analyze_sector(stock_data)
        
        if request.benchmark_symbols:
            response.comparative_analysis = await self._comparative_analysis(
                request.stock_symbol, request.benchmark_symbols, historical_data
            )
        
        # Calcula score e recomendação final
        response.score, response.recommendation, response.confidence = await self._calculate_final_score(response)
        response.summary = await self._generate_summary(response)
        
        return response
    
    async def _get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Busca dados atuais da ação"""
        # Simula busca de dados (integração com Data Service)
        return {
            'symbol': symbol,
            'current_price': 25.50,
            'market_cap': 85000000000,
            'pe_ratio': 12.5,
            'pb_ratio': 1.8,
            'dividend_yield': 0.045,
            'roe': 0.15,
            'roa': 0.08,
            'debt_to_equity': 0.65,
            'current_ratio': 1.2,
            'quick_ratio': 0.9,
            'revenue': 45000000000,
            'net_income': 3500000000,
            'total_assets': 125000000000,
            'total_debt': 35000000000,
            'shareholders_equity': 55000000000,
            'free_cash_flow': 4200000000,
            'operating_cash_flow': 6800000000,
            'shares_outstanding': 3300000000,
            'book_value_per_share': 16.67,
            'earnings_per_share': 1.06,
            'revenue_growth': 0.08,
            'earnings_growth': 0.12,
            'sector': 'Energy',
            'industry': 'Oil & Gas',
            'beta': 1.15
        }
    
    async def _get_historical_data(self, symbol: str, days: int) -> pd.DataFrame:
        """Busca dados históricos da ação"""
        # Simula dados históricos
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        np.random.seed(42)  # Para resultados consistentes
        
        # Gera preços com random walk
        returns = np.random.normal(0.0008, 0.02, days)  # Retorno médio diário de 0.08% com volatilidade de 2%
        prices = [25.0]  # Preço inicial
        
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        volumes = np.random.normal(1000000, 200000, days)
        volumes = np.maximum(volumes, 100000)  # Volume mínimo
        
        return pd.DataFrame({
            'date': dates,
            'close': prices,
            'volume': volumes,
            'high': [p * (1 + np.random.uniform(0, 0.03)) for p in prices],
            'low': [p * (1 - np.random.uniform(0, 0.03)) for p in prices],
            'open': [p * (1 + np.random.uniform(-0.01, 0.01)) for p in prices]
        })
    
    async def _calculate_financial_ratios(self, stock_data: Dict, historical_data: pd.DataFrame) -> Dict[str, float]:
        """Calcula 25+ indicadores financeiros fundamentalistas"""
        ratios = {}
        
        # Indicadores de Liquidez
        ratios['current_ratio'] = stock_data['current_ratio']
        ratios['quick_ratio'] = stock_data['quick_ratio']
        ratios['cash_ratio'] = 0.45  # Simulado
        ratios['operating_cash_flow_ratio'] = stock_data['operating_cash_flow'] / stock_data['total_debt']
        
        # Indicadores de Atividade/Eficiência
        ratios['asset_turnover'] = stock_data['revenue'] / stock_data['total_assets']
        ratios['inventory_turnover'] = 8.5  # Simulado
        ratios['receivables_turnover'] = 12.3  # Simulado
        ratios['working_capital_turnover'] = stock_data['revenue'] / (stock_data['total_assets'] * 0.3)
        
        # Indicadores de Endividamento
        ratios['debt_to_equity'] = stock_data['debt_to_equity']
        ratios['debt_to_assets'] = stock_data['total_debt'] / stock_data['total_assets']
        ratios['equity_ratio'] = stock_data['shareholders_equity'] / stock_data['total_assets']
        ratios['debt_service_coverage'] = stock_data['operating_cash_flow'] / (stock_data['total_debt'] * 0.1)
        ratios['interest_coverage'] = stock_data['net_income'] / (stock_data['total_debt'] * 0.05)
        
        # Indicadores de Rentabilidade
        ratios['roe'] = stock_data['roe']
        ratios['roa'] = stock_data['roa']
        ratios['roi'] = stock_data['net_income'] / (stock_data['total_assets'] - stock_data['total_debt'])
        ratios['gross_margin'] = 0.35  # Simulado
        ratios['operating_margin'] = stock_data['net_income'] / stock_data['revenue'] * 1.4
        ratios['net_margin'] = stock_data['net_income'] / stock_data['revenue']
        ratios['ebitda_margin'] = ratios['operating_margin'] * 1.2
        
        # Indicadores de Mercado
        ratios['pe_ratio'] = stock_data['pe_ratio']
        ratios['pb_ratio'] = stock_data['pb_ratio']
        ratios['ps_ratio'] = stock_data['market_cap'] / stock_data['revenue']
        ratios['ev_ebitda'] = (stock_data['market_cap'] + stock_data['total_debt']) / (stock_data['net_income'] * 1.4)
        ratios['dividend_yield'] = stock_data['dividend_yield']
        ratios['dividend_payout_ratio'] = stock_data['dividend_yield'] * stock_data['pe_ratio']
        
        # Indicadores de Crescimento
        ratios['revenue_growth'] = stock_data['revenue_growth']
        ratios['earnings_growth'] = stock_data['earnings_growth']
        ratios['book_value_growth'] = 0.10  # Simulado
        ratios['dividend_growth'] = 0.08  # Simulado
        
        # Indicadores de Qualidade
        ratios['altman_z_score'] = self._calculate_altman_z_score(stock_data)
        ratios['piotroski_score'] = self._calculate_piotroski_score(stock_data)
        
        return ratios
    
    async def _calculate_valuation_metrics(self, stock_data: Dict, historical_data: pd.DataFrame) -> Dict[str, float]:
        """Calcula métricas de valuation avançadas"""
        metrics = {}
        
        # Modelos de Valuation
        metrics['dcf_value'] = await self._calculate_dcf_value(stock_data)
        metrics['graham_number'] = math.sqrt(22.5 * stock_data['earnings_per_share'] * stock_data['book_value_per_share'])
        metrics['lynch_fair_value'] = stock_data['earnings_growth'] * 100 / stock_data['pe_ratio']
        
        # Múltiplos de Mercado
        metrics['peg_ratio'] = stock_data['pe_ratio'] / (stock_data['earnings_growth'] * 100)
        metrics['price_to_fcf'] = stock_data['market_cap'] / stock_data['free_cash_flow']
        metrics['ev_revenue'] = (stock_data['market_cap'] + stock_data['total_debt']) / stock_data['revenue']
        metrics['price_to_book_tangible'] = stock_data['pb_ratio'] * 1.1  # Ajuste para ativos tangíveis
        
        # Valor Intrínseco
        metrics['intrinsic_value'] = await self._calculate_intrinsic_value(stock_data)
        metrics['margin_of_safety'] = (metrics['intrinsic_value'] - stock_data['current_price']) / metrics['intrinsic_value']
        
        # Métricas de Qualidade do Negócio
        metrics['roic'] = stock_data['net_income'] / (stock_data['shareholders_equity'] + stock_data['total_debt'])
        metrics['economic_moat_score'] = await self._calculate_moat_score(stock_data)
        
        return metrics
    
    async def _calculate_risk_metrics(self, stock_data: Dict, historical_data: pd.DataFrame, confidence_level: float) -> Dict[str, float]:
        """Calcula métricas de risco avançadas"""
        metrics = {}
        
        # Calcula retornos
        returns = historical_data['close'].pct_change().dropna()
        
        # Volatilidade
        metrics['volatility_daily'] = returns.std()
        metrics['volatility_annual'] = returns.std() * math.sqrt(252)
        metrics['volatility_30d'] = returns.tail(30).std() * math.sqrt(252)
        
        # Value at Risk (VaR)
        metrics['var_1d'] = np.percentile(returns, (1 - confidence_level) * 100)
        metrics['var_5d'] = metrics['var_1d'] * math.sqrt(5)
        metrics['var_30d'] = metrics['var_1d'] * math.sqrt(30)
        
        # Expected Shortfall (CVaR)
        var_threshold = metrics['var_1d']
        tail_returns = returns[returns <= var_threshold]
        metrics['cvar_1d'] = tail_returns.mean() if len(tail_returns) > 0 else metrics['var_1d']
        
        # Beta e correlações
        metrics['beta'] = stock_data['beta']
        metrics['correlation_market'] = 0.75  # Simulado
        
        # Sharpe Ratio
        excess_returns = returns.mean() - (self.risk_free_rate / 252)
        metrics['sharpe_ratio'] = excess_returns / returns.std() if returns.std() > 0 else 0
        
        # Sortino Ratio
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() if len(downside_returns) > 0 else returns.std()
        metrics['sortino_ratio'] = excess_returns / downside_std if downside_std > 0 else 0
        
        # Maximum Drawdown
        cumulative_returns = (1 + returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdowns = (cumulative_returns - rolling_max) / rolling_max
        metrics['max_drawdown'] = drawdowns.min()
        
        # Calmar Ratio
        annual_return = returns.mean() * 252
        metrics['calmar_ratio'] = annual_return / abs(metrics['max_drawdown']) if metrics['max_drawdown'] != 0 else 0
        
        # Skewness e Kurtosis
        metrics['skewness'] = returns.skew()
        metrics['kurtosis'] = returns.kurtosis()
        
        # Risco de Liquidez
        avg_volume = historical_data['volume'].mean()
        metrics['liquidity_risk'] = stock_data['market_cap'] / (avg_volume * stock_data['current_price'] * 252)
        
        # Risco Financeiro
        metrics['financial_risk_score'] = await self._calculate_financial_risk_score(stock_data)
        
        return metrics
    
    async def _calculate_technical_indicators(self, historical_data: pd.DataFrame) -> Dict[str, float]:
        """Calcula indicadores técnicos"""
        indicators = {}
        prices = historical_data['close']
        
        # Médias Móveis
        indicators['sma_20'] = prices.tail(20).mean()
        indicators['sma_50'] = prices.tail(50).mean()
        indicators['sma_200'] = prices.tail(200).mean()
        
        # EMA
        indicators['ema_12'] = prices.ewm(span=12).mean().iloc[-1]
        indicators['ema_26'] = prices.ewm(span=26).mean().iloc[-1]
        
        # MACD
        macd_line = indicators['ema_12'] - indicators['ema_26']
        indicators['macd'] = macd_line
        indicators['macd_signal'] = 0.85 * macd_line  # Simulado
        
        # RSI
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        indicators['rsi'] = 100 - (100 / (1 + rs.iloc[-1]))
        
        # Bollinger Bands
        sma_20 = prices.tail(20).mean()
        std_20 = prices.tail(20).std()
        indicators['bb_upper'] = sma_20 + (2 * std_20)
        indicators['bb_lower'] = sma_20 - (2 * std_20)
        indicators['bb_position'] = (prices.iloc[-1] - indicators['bb_lower']) / (indicators['bb_upper'] - indicators['bb_lower'])
        
        # Stochastic
        high_14 = historical_data['high'].tail(14).max()
        low_14 = historical_data['low'].tail(14).min()
        indicators['stoch_k'] = ((prices.iloc[-1] - low_14) / (high_14 - low_14)) * 100
        
        # Volume indicators
        indicators['volume_sma_20'] = historical_data['volume'].tail(20).mean()
        indicators['volume_ratio'] = historical_data['volume'].iloc[-1] / indicators['volume_sma_20']
        
        return indicators
    
    async def _analyze_sector(self, stock_data: Dict) -> Dict[str, Any]:
        """Análise setorial"""
        sector_analysis = {
            'sector': stock_data['sector'],
            'industry': stock_data['industry'],
            'sector_pe_avg': 14.2,  # Simulado
            'sector_pb_avg': 2.1,   # Simulado
            'sector_roe_avg': 0.13, # Simulado
            'relative_pe': stock_data['pe_ratio'] / 14.2,
            'relative_pb': stock_data['pb_ratio'] / 2.1,
            'relative_roe': stock_data['roe'] / 0.13,
            'sector_rank': 'Top 25%',  # Simulado
            'industry_trends': {
                'growth_outlook': 'Positive',
                'regulatory_environment': 'Stable',
                'competitive_intensity': 'High'
            }
        }
        
        return sector_analysis
    
    async def _comparative_analysis(self, symbol: str, benchmarks: List[str], historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Análise comparativa com benchmarks"""
        returns = historical_data['close'].pct_change().dropna()
        
        comparative = {
            'symbol': symbol,
            'benchmarks': benchmarks,
            'performance_1m': returns.tail(21).mean() * 21,  # Último mês
            'performance_3m': returns.tail(63).mean() * 63,  # Últimos 3 meses
            'performance_1y': returns.mean() * 252,          # Último ano
            'volatility_vs_market': returns.std() / 0.015,   # vs volatilidade do mercado
            'correlation_with_benchmarks': {},
            'relative_strength': 1.15,  # Simulado
            'alpha': 0.02,  # Simulado
            'tracking_error': 0.08  # Simulado
        }
        
        # Simula correlações com benchmarks
        for benchmark in benchmarks:
            comparative['correlation_with_benchmarks'][benchmark] = np.random.uniform(0.6, 0.9)
        
        return comparative
    
    def _calculate_altman_z_score(self, stock_data: Dict) -> float:
        """Calcula Altman Z-Score para risco de falência"""
        # Z = 1.2*A + 1.4*B + 3.3*C + 0.6*D + 1.0*E
        # A = Working Capital / Total Assets
        # B = Retained Earnings / Total Assets  
        # C = EBIT / Total Assets
        # D = Market Value Equity / Total Liabilities
        # E = Sales / Total Assets
        
        working_capital = stock_data['total_assets'] * 0.25  # Simulado
        retained_earnings = stock_data['shareholders_equity'] * 0.6  # Simulado
        ebit = stock_data['net_income'] * 1.3  # Simulado
        
        a = working_capital / stock_data['total_assets']
        b = retained_earnings / stock_data['total_assets']
        c = ebit / stock_data['total_assets']
        d = stock_data['market_cap'] / stock_data['total_debt']
        e = stock_data['revenue'] / stock_data['total_assets']
        
        z_score = 1.2*a + 1.4*b + 3.3*c + 0.6*d + 1.0*e
        return z_score
    
    def _calculate_piotroski_score(self, stock_data: Dict) -> int:
        """Calcula Piotroski F-Score (0-9)"""
        score = 0
        
        # Rentabilidade (4 pontos)
        if stock_data['roa'] > 0: score += 1
        if stock_data['operating_cash_flow'] > 0: score += 1
        if stock_data['roa'] > 0.08: score += 1  # ROA melhorando
        if stock_data['operating_cash_flow'] > stock_data['net_income']: score += 1
        
        # Alavancagem/Liquidez (3 pontos)
        if stock_data['debt_to_equity'] < 0.5: score += 1  # Dívida diminuindo
        if stock_data['current_ratio'] > 1.5: score += 1  # Liquidez melhorando
        if stock_data['shares_outstanding'] < 3500000000: score += 1  # Sem diluição
        
        # Eficiência Operacional (2 pontos)
        if stock_data['revenue'] / stock_data['total_assets'] > 0.35: score += 1  # Margem bruta melhorando
        if stock_data['revenue'] / stock_data['total_assets'] > 0.30: score += 1  # Giro de ativos melhorando
        
        return score
    
    async def _calculate_dcf_value(self, stock_data: Dict) -> float:
        """Calcula valor por Fluxo de Caixa Descontado"""
        # Modelo DCF simplificado
        fcf = stock_data['free_cash_flow']
        growth_rate = min(stock_data['earnings_growth'], 0.15)  # Cap no crescimento
        terminal_growth = 0.03  # Crescimento perpétuo
        discount_rate = self.risk_free_rate + (stock_data['beta'] * 0.06)  # CAPM
        
        # Projeta FCF por 5 anos
        projected_fcf = []
        for year in range(1, 6):
            projected_fcf.append(fcf * ((1 + growth_rate) ** year))
        
        # Valor terminal
        terminal_fcf = projected_fcf[-1] * (1 + terminal_growth)
        terminal_value = terminal_fcf / (discount_rate - terminal_growth)
        
        # Valor presente
        pv_fcf = sum([cf / ((1 + discount_rate) ** (i + 1)) for i, cf in enumerate(projected_fcf)])
        pv_terminal = terminal_value / ((1 + discount_rate) ** 5)
        
        enterprise_value = pv_fcf + pv_terminal
        equity_value = enterprise_value - stock_data['total_debt']
        value_per_share = equity_value / stock_data['shares_outstanding']
        
        return value_per_share
    
    async def _calculate_intrinsic_value(self, stock_data: Dict) -> float:
        """Calcula valor intrínseco usando múltiplos métodos"""
        # Método 1: DCF
        dcf_value = await self._calculate_dcf_value(stock_data)
        
        # Método 2: Graham Formula
        eps = stock_data['earnings_per_share']
        growth = stock_data['earnings_growth'] * 100
        graham_value = eps * (8.5 + 2 * growth) * 4.4 / (self.risk_free_rate * 100)
        
        # Método 3: Dividend Discount Model (se aplicável)
        if stock_data['dividend_yield'] > 0:
            dividend_per_share = stock_data['current_price'] * stock_data['dividend_yield']
            dividend_growth = 0.05  # Assumido
            required_return = self.risk_free_rate + (stock_data['beta'] * 0.06)
            ddm_value = dividend_per_share * (1 + dividend_growth) / (required_return - dividend_growth)
        else:
            ddm_value = dcf_value
        
        # Média ponderada dos métodos
        intrinsic_value = (dcf_value * 0.5) + (graham_value * 0.3) + (ddm_value * 0.2)
        return intrinsic_value
    
    async def _calculate_moat_score(self, stock_data: Dict) -> float:
        """Calcula score de vantagem competitiva (moat)"""
        score = 0.0
        
        # ROE consistentemente alto
        if stock_data['roe'] > 0.15: score += 2.0
        elif stock_data['roe'] > 0.10: score += 1.0
        
        # Margens altas
        net_margin = stock_data['net_income'] / stock_data['revenue']
        if net_margin > 0.15: score += 2.0
        elif net_margin > 0.10: score += 1.0
        
        # Baixo endividamento
        if stock_data['debt_to_equity'] < 0.3: score += 2.0
        elif stock_data['debt_to_equity'] < 0.6: score += 1.0
        
        # Crescimento consistente
        if stock_data['revenue_growth'] > 0.10: score += 1.5
        if stock_data['earnings_growth'] > 0.10: score += 1.5
        
        # Free cash flow forte
        fcf_margin = stock_data['free_cash_flow'] / stock_data['revenue']
        if fcf_margin > 0.10: score += 1.0
        
        return min(score, 10.0)  # Score máximo de 10
    
    async def _calculate_financial_risk_score(self, stock_data: Dict) -> float:
        """Calcula score de risco financeiro (0-10, menor é melhor)"""
        risk_score = 0.0
        
        # Risco de liquidez
        if stock_data['current_ratio'] < 1.0: risk_score += 2.0
        elif stock_data['current_ratio'] < 1.5: risk_score += 1.0
        
        # Risco de endividamento
        if stock_data['debt_to_equity'] > 1.0: risk_score += 3.0
        elif stock_data['debt_to_equity'] > 0.7: risk_score += 1.5
        
        # Risco de rentabilidade
        if stock_data['roe'] < 0.05: risk_score += 2.0
        elif stock_data['roe'] < 0.10: risk_score += 1.0
        
        # Risco de cobertura de juros
        interest_coverage = stock_data['net_income'] / (stock_data['total_debt'] * 0.05)
        if interest_coverage < 2.0: risk_score += 2.0
        elif interest_coverage < 5.0: risk_score += 1.0
        
        # Risco de volatilidade (baseado no beta)
        if stock_data['beta'] > 1.5: risk_score += 1.0
        elif stock_data['beta'] > 1.2: risk_score += 0.5
        
        return min(risk_score, 10.0)
    
    async def _calculate_final_score(self, response: AdvancedAnalysisResponse) -> Tuple[float, str, float]:
        """Calcula score final e recomendação"""
        score = 5.0  # Score neutro
        confidence = 0.5
        
        # Análise de ratios financeiros
        if response.financial_ratios:
            ratios = response.financial_ratios
            
            # Rentabilidade
            if ratios.get('roe', 0) > 0.15: score += 1.0
            if ratios.get('roa', 0) > 0.08: score += 0.5
            if ratios.get('net_margin', 0) > 0.10: score += 0.5
            
            # Liquidez
            if ratios.get('current_ratio', 0) > 1.5: score += 0.5
            if ratios.get('quick_ratio', 0) > 1.0: score += 0.3
            
            # Endividamento
            if ratios.get('debt_to_equity', 1) < 0.5: score += 0.7
            elif ratios.get('debt_to_equity', 1) > 1.0: score -= 1.0
            
            # Crescimento
            if ratios.get('revenue_growth', 0) > 0.10: score += 0.8
            if ratios.get('earnings_growth', 0) > 0.10: score += 0.8
            
            # Qualidade
            if ratios.get('piotroski_score', 0) >= 7: score += 1.0
            elif ratios.get('piotroski_score', 0) <= 3: score -= 1.0
            
            confidence += 0.2
        
        # Análise de valuation
        if response.valuation_metrics:
            valuation = response.valuation_metrics
            
            # Margem de segurança
            margin_of_safety = valuation.get('margin_of_safety', 0)
            if margin_of_safety > 0.2: score += 1.5
            elif margin_of_safety > 0.1: score += 0.8
            elif margin_of_safety < -0.2: score -= 1.5
            
            # PEG ratio
            peg = valuation.get('peg_ratio', 1)
            if peg < 1.0: score += 0.5
            elif peg > 2.0: score -= 0.5
            
            confidence += 0.2
        
        # Análise de risco
        if response.risk_metrics:
            risk = response.risk_metrics
            
            # Sharpe ratio
            sharpe = risk.get('sharpe_ratio', 0)
            if sharpe > 1.0: score += 0.5
            elif sharpe < 0: score -= 0.5
            
            # Volatilidade
            volatility = risk.get('volatility_annual', 0.2)
            if volatility < 0.15: score += 0.3
            elif volatility > 0.30: score -= 0.5
            
            # Risco financeiro
            financial_risk = risk.get('financial_risk_score', 5)
            if financial_risk < 3: score += 0.5
            elif financial_risk > 7: score -= 1.0
            
            confidence += 0.15
        
        # Normaliza score (0-10)
        score = max(0, min(10, score))
        
        # Determina recomendação
        if score >= 7.5:
            recommendation = "STRONG_BUY"
        elif score >= 6.5:
            recommendation = "BUY"
        elif score >= 4.5:
            recommendation = "HOLD"
        elif score >= 3.0:
            recommendation = "SELL"
        else:
            recommendation = "STRONG_SELL"
        
        # Normaliza confiança (0-1)
        confidence = min(1.0, confidence)
        
        return score, recommendation, confidence
    
    async def _generate_summary(self, response: AdvancedAnalysisResponse) -> str:
        """Gera resumo da análise"""
        summary_parts = []
        
        # Introdução
        summary_parts.append(f"Análise de {response.stock_symbol} realizada em {response.timestamp.strftime('%d/%m/%Y')}.")
        
        # Score e recomendação
        summary_parts.append(f"Score geral: {response.score:.1f}/10 - Recomendação: {response.recommendation}")
        
        # Pontos fortes e fracos
        if response.financial_ratios:
            ratios = response.financial_ratios
            
            strengths = []
            weaknesses = []
            
            if ratios.get('roe', 0) > 0.15:
                strengths.append("ROE elevado")
            if ratios.get('debt_to_equity', 1) < 0.5:
                strengths.append("baixo endividamento")
            if ratios.get('current_ratio', 0) > 1.5:
                strengths.append("boa liquidez")
            
            if ratios.get('roe', 0) < 0.08:
                weaknesses.append("ROE baixo")
            if ratios.get('debt_to_equity', 1) > 1.0:
                weaknesses.append("alto endividamento")
            if ratios.get('current_ratio', 0) < 1.0:
                weaknesses.append("liquidez comprometida")
            
            if strengths:
                summary_parts.append(f"Pontos fortes: {', '.join(strengths)}.")
            if weaknesses:
                summary_parts.append(f"Pontos de atenção: {', '.join(weaknesses)}.")
        
        # Valuation
        if response.valuation_metrics:
            margin = response.valuation_metrics.get('margin_of_safety', 0)
            if margin > 0.1:
                summary_parts.append("Ação apresenta margem de segurança atrativa.")
            elif margin < -0.1:
                summary_parts.append("Ação pode estar sobrevalorizada.")
        
        # Risco
        if response.risk_metrics:
            volatility = response.risk_metrics.get('volatility_annual', 0.2)
            if volatility > 0.25:
                summary_parts.append("Atenção para alta volatilidade.")
            
            sharpe = response.risk_metrics.get('sharpe_ratio', 0)
            if sharpe > 1.0:
                summary_parts.append("Boa relação risco-retorno.")
        
        return " ".join(summary_parts)

# Instância global do analisador
analyzer = FinancialAnalyzer()

# Dependency para autenticação
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Implementação simplificada - em produção, validar JWT
    return {"user_id": "test_user", "email": "test@example.com"}

@app.on_event("startup")
async def startup_event():
    """Inicialização do serviço"""
    global cache, kafka_client, redis_client
    
    logger.info("Starting Analysis Service...")
    
    # Inicializa cache
    cache = AdvancedCache(
        redis_url="redis://localhost:6379",
        l1_max_size=1000,
        default_ttl=3600
    )
    await cache.initialize()
    
    # Inicializa Kafka
    kafka_client = KafkaClient(
        bootstrap_servers="localhost:9092",
        group_id="analysis-service"
    )
    await kafka_client.initialize()
    
    # Inicializa Redis
    redis_client = redis.from_url("redis://localhost:6379")
    
    logger.info("Analysis Service started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Limpeza do serviço"""
    if cache:
        await cache.close()
    if kafka_client:
        await kafka_client.close()
    if redis_client:
        await redis_client.close()

@app.get("/health")
async def health_check():
    """Health check do serviço"""
    return {
        "status": "healthy",
        "service": "analysis-service",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/metrics")
async def metrics():
    """Métricas Prometheus"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/analyze", response_model=AdvancedAnalysisResponse)
async def analyze_stock(
    request: AdvancedAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Executa análise financeira avançada"""
    analysis_requests.labels(analysis_type=request.analysis_type).inc()
    
    with analysis_duration.labels(analysis_type=request.analysis_type).time():
        active_analyses.inc()
        
        try:
            # Verifica cache primeiro
            cache_key = f"analysis:{request.stock_symbol}:{request.analysis_type}:{hash(str(request.dict()))}"
            
            if cache:
                cached_result = await cache.get(cache_key)
                if cached_result:
                    cache_hit_ratio.set(0.8)  # Atualiza métrica
                    return cached_result
            
            # Executa análise
            result = await analyzer.analyze_stock(request)
            
            # Salva no cache
            if cache:
                await cache.set(
                    cache_key, 
                    result.dict(), 
                    ttl=3600,
                    key_type="analysis"
                )
            
            # Envia evento assíncrono
            if kafka_client:
                background_tasks.add_task(
                    kafka_client.send_message,
                    "analysis-completed",
                    {
                        "stock_symbol": request.stock_symbol,
                        "analysis_type": request.analysis_type,
                        "score": result.score,
                        "recommendation": result.recommendation,
                        "user_id": current_user["user_id"],
                        "timestamp": datetime.now().isoformat()
                    }
                )
            
            return result
            
        except Exception as e:
            analysis_errors.labels(error_type=type(e).__name__).inc()
            logger.error(f"Analysis error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
        
        finally:
            active_analyses.dec()

@app.get("/indicators")
async def list_indicators():
    """Lista todos os indicadores disponíveis"""
    return {
        "financial_ratios": [
            "current_ratio", "quick_ratio", "cash_ratio", "operating_cash_flow_ratio",
            "asset_turnover", "inventory_turnover", "receivables_turnover", "working_capital_turnover",
            "debt_to_equity", "debt_to_assets", "equity_ratio", "debt_service_coverage", "interest_coverage",
            "roe", "roa", "roi", "gross_margin", "operating_margin", "net_margin", "ebitda_margin",
            "pe_ratio", "pb_ratio", "ps_ratio", "ev_ebitda", "dividend_yield", "dividend_payout_ratio",
            "revenue_growth", "earnings_growth", "book_value_growth", "dividend_growth",
            "altman_z_score", "piotroski_score"
        ],
        "valuation_metrics": [
            "dcf_value", "graham_number", "lynch_fair_value", "peg_ratio", "price_to_fcf",
            "ev_revenue", "price_to_book_tangible", "intrinsic_value", "margin_of_safety",
            "roic", "economic_moat_score"
        ],
        "risk_metrics": [
            "volatility_daily", "volatility_annual", "volatility_30d", "var_1d", "var_5d", "var_30d",
            "cvar_1d", "beta", "correlation_market", "sharpe_ratio", "sortino_ratio",
            "max_drawdown", "calmar_ratio", "skewness", "kurtosis", "liquidity_risk", "financial_risk_score"
        ],
        "technical_indicators": [
            "sma_20", "sma_50", "sma_200", "ema_12", "ema_26", "macd", "macd_signal",
            "rsi", "bb_upper", "bb_lower", "bb_position", "stoch_k", "volume_sma_20", "volume_ratio"
        ]
    }

@app.get("/stats")
async def get_stats():
    """Estatísticas do serviço"""
    stats = {
        "service": "analysis-service",
        "uptime": "running",
        "total_analyses": 0,
        "cache_stats": {}
    }
    
    if cache:
        stats["cache_stats"] = await cache.get_stats()
    
    return stats

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    )

