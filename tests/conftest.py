"""
Configuração global dos testes
"""

import pytest
import asyncio
import httpx
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock
import os
import sys

# Adicionar path dos microserviços
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'microservices'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

@pytest.fixture(scope="session")
def event_loop():
    """Cria event loop para testes assíncronos"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Cliente HTTP para testes"""
    async with httpx.AsyncClient() as client:
        yield client

@pytest.fixture
def mock_redis():
    """Mock do Redis"""
    mock = Mock()
    mock.ping.return_value = True
    mock.get.return_value = None
    mock.set.return_value = True
    mock.delete.return_value = True
    mock.exists.return_value = False
    return mock

@pytest.fixture
def mock_kafka_producer():
    """Mock do Kafka Producer"""
    mock = AsyncMock()
    mock.send_analysis_result = AsyncMock(return_value=True)
    mock.send_complete_analysis = AsyncMock(return_value=True)
    return mock

@pytest.fixture
def mock_service_client():
    """Mock do Service Client"""
    mock = AsyncMock()
    mock.validate_token.return_value = {"valid": True, "user_id": 1, "email": "test@example.com"}
    mock.get_stock_data.return_value = {
        "symbol": "PETR4.SA",
        "pe_ratio": 15.5,
        "price_to_book": 1.2,
        "debt_to_equity": 0.8,
        "roe": 18.5,
        "current_ratio": 1.5,
        "dividend_yield": 4.2,
        "payout_ratio": 65.0,
        "earnings_growth": 12.0,
        "revenue_growth": 8.5,
        "profit_margin": 15.2,
        "beta": 1.1,
        "market_cap": 50000000000,
        "free_cash_flow": 1000000000
    }
    mock.analyze_with_methodology.return_value = {
        "symbol": "PETR4.SA",
        "score": 75,
        "recomendacao": "COMPRA",
        "metodologia_aplicada": "Warren Buffett",
        "pontos_fortes": ["P/E atrativo", "ROE alto"],
        "pontos_fracos": [],
        "justificativa": "Empresa com fundamentos sólidos"
    }
    return mock

@pytest.fixture
def sample_stock_data():
    """Dados de exemplo para testes"""
    return {
        "symbol": "PETR4.SA",
        "pe_ratio": 15.5,
        "price_to_book": 1.2,
        "debt_to_equity": 0.8,
        "roe": 18.5,
        "current_ratio": 1.5,
        "dividend_yield": 4.2,
        "payout_ratio": 65.0,
        "earnings_growth": 12.0,
        "revenue_growth": 8.5,
        "profit_margin": 15.2,
        "beta": 1.1,
        "market_cap": 50000000000,
        "free_cash_flow": 1000000000
    }

@pytest.fixture
def sample_user_data():
    """Dados de usuário para testes"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "full_name": "Test User"
    }

@pytest.fixture
def auth_headers():
    """Headers de autenticação para testes"""
    return {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }

@pytest.fixture
def mock_database():
    """Mock do banco de dados"""
    mock = Mock()
    mock.query.return_value = mock
    mock.filter.return_value = mock
    mock.first.return_value = None
    mock.add.return_value = None
    mock.commit.return_value = None
    mock.refresh.return_value = None
    return mock

# Configurações de teste
TEST_DATABASE_URL = "sqlite:///./test.db"
TEST_REDIS_URL = "redis://localhost:6379/1"

# Variáveis de ambiente para testes
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["REDIS_URL"] = TEST_REDIS_URL
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["TESTING"] = "true"

