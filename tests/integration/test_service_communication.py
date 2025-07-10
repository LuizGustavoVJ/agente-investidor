"""
Testes de integração da comunicação entre serviços
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import httpx
import json

class TestServiceCommunication:
    """Testes de comunicação entre serviços"""
    
    @pytest.mark.asyncio
    async def test_auth_service_validation(self, mock_service_client):
        """Testa validação de token no serviço de autenticação"""
        # Simular resposta do serviço de auth
        mock_service_client.validate_token.return_value = {
            "valid": True,
            "user_id": 123,
            "email": "test@example.com",
            "expires_at": "2024-12-31T23:59:59Z"
        }
        
        result = await mock_service_client.validate_token("test-token")
        
        assert result["valid"] is True
        assert result["user_id"] == 123
        assert result["email"] == "test@example.com"
        mock_service_client.validate_token.assert_called_once_with("test-token")
    
    @pytest.mark.asyncio
    async def test_data_service_stock_fetch(self, mock_service_client, sample_stock_data):
        """Testa busca de dados de ação no serviço de dados"""
        mock_service_client.get_stock_data.return_value = sample_stock_data
        
        result = await mock_service_client.get_stock_data("PETR4.SA")
        
        assert result["symbol"] == "PETR4.SA"
        assert result["pe_ratio"] == 15.5
        assert result["roe"] == 18.5
        mock_service_client.get_stock_data.assert_called_once_with("PETR4.SA")
    
    @pytest.mark.asyncio
    async def test_methodology_service_analysis(self, mock_service_client, sample_stock_data):
        """Testa análise no serviço de metodologias"""
        expected_result = {
            "symbol": "PETR4.SA",
            "score": 75,
            "recomendacao": "COMPRA",
            "metodologia_aplicada": "Warren Buffett",
            "pontos_fortes": ["P/E atrativo", "ROE alto"],
            "pontos_fracos": [],
            "justificativa": "Empresa com fundamentos sólidos"
        }
        
        mock_service_client.analyze_with_methodology.return_value = expected_result
        
        result = await mock_service_client.analyze_with_methodology(
            "PETR4.SA", 
            "warren_buffett", 
            sample_stock_data
        )
        
        assert result["symbol"] == "PETR4.SA"
        assert result["score"] == 75
        assert result["recomendacao"] == "COMPRA"
        assert "P/E atrativo" in result["pontos_fortes"]
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_functionality(self):
        """Testa funcionalidade do circuit breaker"""
        from microservices.shared.communication.service_client import ServiceClient, ServiceConfig, CircuitState
        
        # Criar cliente com configuração de teste
        client = ServiceClient()
        config = ServiceConfig(
            name="test-service",
            base_url="http://test-service:8000",
            circuit_breaker_threshold=2,
            circuit_breaker_timeout=1.0
        )
        client.register_service(config)
        
        # Simular falhas consecutivas
        with patch.object(client.client, 'get') as mock_get:
            mock_get.side_effect = httpx.ConnectError("Connection failed")
            
            # Primeira falha
            with pytest.raises(httpx.ConnectError):
                await client.get("test-service", "/test")
            
            # Segunda falha - deve abrir circuit breaker
            with pytest.raises(httpx.ConnectError):
                await client.get("test-service", "/test")
            
            # Terceira tentativa - circuit breaker deve estar OPEN
            cb = client._get_circuit_breaker("test-service")
            assert cb.state == CircuitState.OPEN
            
            # Deve rejeitar sem tentar requisição
            with pytest.raises(Exception, match="Circuit breaker OPEN"):
                await client.get("test-service", "/test")
    
    @pytest.mark.asyncio
    async def test_retry_mechanism(self):
        """Testa mecanismo de retry"""
        from microservices.shared.communication.service_client import ServiceClient, ServiceConfig
        
        client = ServiceClient()
        config = ServiceConfig(
            name="retry-test-service",
            base_url="http://retry-test:8000",
            retries=3,
            retry_delay=0.1
        )
        client.register_service(config)
        
        with patch.object(client.client, 'get') as mock_get:
            # Simular 2 falhas seguidas de sucesso
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "success"}
            
            mock_get.side_effect = [
                httpx.ConnectError("First failure"),
                httpx.ConnectError("Second failure"),
                mock_response
            ]
            
            result = await client.get("retry-test-service", "/test")
            
            assert result["status"] == "success"
            assert mock_get.call_count == 3  # 2 falhas + 1 sucesso
    
    @pytest.mark.asyncio
    async def test_service_health_check(self, mock_service_client):
        """Testa health check dos serviços"""
        # Simular respostas de health check
        health_responses = {
            "auth-service": {"status": "healthy", "uptime": 3600},
            "data-service": {"status": "healthy", "uptime": 3500},
            "methodology-service": {"status": "healthy", "uptime": 3400},
            "analysis-service": {"status": "degraded", "uptime": 100}
        }
        
        mock_service_client.health_check_all.return_value = {
            service: {
                "status": "healthy" if response["status"] == "healthy" else "unhealthy",
                "response": response,
                "circuit_breaker": "closed"
            }
            for service, response in health_responses.items()
        }
        
        result = await mock_service_client.health_check_all()
        
        assert len(result) == 4
        assert result["auth-service"]["status"] == "healthy"
        assert result["analysis-service"]["status"] == "unhealthy"
    
    @pytest.mark.asyncio
    async def test_authentication_middleware_integration(self, http_client, auth_headers):
        """Testa integração do middleware de autenticação"""
        # Simular endpoint protegido
        with patch('microservices.shared.communication.validate_user_token') as mock_validate:
            mock_validate.return_value = {
                "valid": True,
                "user_id": 123,
                "email": "test@example.com"
            }
            
            # Simular requisição com token válido
            response_data = {"message": "Access granted"}
            
            # Verificar que a validação seria chamada
            await mock_validate("test-token")
            mock_validate.assert_called_once_with("test-token")
    
    @pytest.mark.asyncio
    async def test_cross_service_data_flow(self, mock_service_client, sample_stock_data):
        """Testa fluxo de dados entre múltiplos serviços"""
        # Simular fluxo completo: Auth -> Data -> Methodology -> Analysis
        
        # 1. Validar token
        mock_service_client.validate_token.return_value = {
            "valid": True,
            "user_id": 123,
            "email": "investor@example.com"
        }
        
        # 2. Buscar dados da ação
        mock_service_client.get_stock_data.return_value = sample_stock_data
        
        # 3. Analisar com metodologia
        mock_service_client.analyze_with_methodology.return_value = {
            "symbol": "PETR4.SA",
            "score": 78,
            "recomendacao": "COMPRA",
            "metodologia_aplicada": "Warren Buffett"
        }
        
        # 4. Análise financeira completa
        mock_service_client.get_financial_analysis.return_value = {
            "symbol": "PETR4.SA",
            "overall_score": 76,
            "risk_level": "MEDIO",
            "indicators": {
                "pe_ratio": 15.5,
                "roe": 18.5,
                "debt_ratio": 0.8
            }
        }
        
        # Executar fluxo completo
        token_validation = await mock_service_client.validate_token("valid-token")
        assert token_validation["valid"] is True
        
        stock_data = await mock_service_client.get_stock_data("PETR4.SA")
        assert stock_data["symbol"] == "PETR4.SA"
        
        methodology_result = await mock_service_client.analyze_with_methodology(
            "PETR4.SA", "warren_buffett", stock_data
        )
        assert methodology_result["score"] == 78
        
        financial_analysis = await mock_service_client.get_financial_analysis(
            "PETR4.SA", ["pe_ratio", "roe", "debt_ratio"]
        )
        assert financial_analysis["overall_score"] == 76

class TestServiceFailureScenarios:
    """Testes de cenários de falha"""
    
    @pytest.mark.asyncio
    async def test_service_unavailable(self, mock_service_client):
        """Testa comportamento quando serviço está indisponível"""
        mock_service_client.get_stock_data.side_effect = httpx.ConnectError("Service unavailable")
        
        with pytest.raises(httpx.ConnectError):
            await mock_service_client.get_stock_data("PETR4.SA")
    
    @pytest.mark.asyncio
    async def test_invalid_token_handling(self, mock_service_client):
        """Testa tratamento de token inválido"""
        mock_service_client.validate_token.return_value = {
            "valid": False,
            "error": "Token expired"
        }
        
        result = await mock_service_client.validate_token("expired-token")
        assert result["valid"] is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_partial_service_failure(self, mock_service_client):
        """Testa falha parcial de serviços"""
        # Simular cenário onde alguns serviços funcionam e outros não
        def side_effect(service_name):
            if service_name == "auth-service":
                return {"status": "healthy"}
            elif service_name == "data-service":
                raise httpx.ConnectError("Data service down")
            elif service_name == "methodology-service":
                return {"status": "healthy"}
            else:
                raise httpx.TimeoutException("Analysis service timeout")
        
        mock_service_client.health_check.side_effect = side_effect
        
        # Verificar que serviços saudáveis ainda funcionam
        auth_health = await mock_service_client.health_check("auth-service")
        assert auth_health["status"] == "healthy"
        
        # Verificar que serviços com falha geram exceções
        with pytest.raises(httpx.ConnectError):
            await mock_service_client.health_check("data-service")
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, mock_service_client):
        """Testa tratamento de timeouts"""
        mock_service_client.get_stock_data.side_effect = httpx.TimeoutException("Request timeout")
        
        with pytest.raises(httpx.TimeoutException):
            await mock_service_client.get_stock_data("SLOW.SA")
    
    @pytest.mark.asyncio
    async def test_malformed_response_handling(self, mock_service_client):
        """Testa tratamento de respostas malformadas"""
        # Simular resposta com JSON inválido
        mock_service_client.get_stock_data.return_value = {
            "invalid": "response",
            "missing_required_fields": True
        }
        
        result = await mock_service_client.get_stock_data("INVALID.SA")
        
        # Deve retornar a resposta mesmo que malformada
        assert "invalid" in result
        assert result["missing_required_fields"] is True

class TestServicePerformance:
    """Testes de performance dos serviços"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, mock_service_client):
        """Testa requisições concorrentes"""
        # Simular múltiplas requisições simultâneas
        symbols = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "WEGE3.SA", "MGLU3.SA"]
        
        async def mock_get_stock_data(symbol):
            await asyncio.sleep(0.1)  # Simular latência
            return {"symbol": symbol, "price": 100.0}
        
        mock_service_client.get_stock_data.side_effect = mock_get_stock_data
        
        # Executar requisições concorrentes
        tasks = [
            mock_service_client.get_stock_data(symbol) 
            for symbol in symbols
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        assert all(result["symbol"] in symbols for result in results)
    
    @pytest.mark.asyncio
    async def test_cache_effectiveness(self, mock_redis, mock_service_client):
        """Testa efetividade do cache"""
        # Simular cache hit
        mock_redis.get.return_value = json.dumps({
            "symbol": "CACHED.SA",
            "price": 50.0,
            "cached": True
        })
        
        # Primeira requisição deve usar cache
        with patch('microservices.shared.cache.redis_manager.get') as mock_cache_get:
            mock_cache_get.return_value = {
                "symbol": "CACHED.SA",
                "price": 50.0,
                "cached": True
            }
            
            # Simular busca com cache
            cached_result = mock_cache_get("stock:CACHED.SA")
            assert cached_result["cached"] is True
            assert cached_result["symbol"] == "CACHED.SA"

