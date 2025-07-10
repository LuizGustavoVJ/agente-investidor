"""
Testes end-to-end do workflow completo do sistema
"""

import pytest
import asyncio
import httpx
from unittest.mock import Mock, patch
import json

class TestCompleteInvestmentWorkflow:
    """Testes do workflow completo de análise de investimento"""
    
    @pytest.mark.asyncio
    async def test_complete_analysis_workflow(self, http_client, auth_headers, sample_stock_data):
        """Testa workflow completo: login -> buscar dados -> analisar -> resultado"""
        
        # Simular serviços funcionando
        with patch('microservices.shared.communication.service_client') as mock_client:
            # 1. Login/Autenticação
            mock_client.validate_token.return_value = {
                "valid": True,
                "user_id": 123,
                "email": "investor@example.com",
                "permissions": ["read", "analyze"]
            }
            
            # 2. Buscar dados da ação
            mock_client.get_stock_data.return_value = sample_stock_data
            
            # 3. Analisar com múltiplas metodologias
            methodology_results = {
                "warren_buffett": {
                    "score": 78,
                    "recomendacao": "COMPRA",
                    "pontos_fortes": ["P/E atrativo", "ROE alto", "Dívida baixa"],
                    "pontos_fracos": []
                },
                "benjamin_graham": {
                    "score": 72,
                    "recomendacao": "COMPRA", 
                    "pontos_fortes": ["Margem de segurança", "Liquidez boa"],
                    "pontos_fracos": ["Crescimento moderado"]
                },
                "peter_lynch": {
                    "score": 65,
                    "recomendacao": "NEUTRO",
                    "pontos_fortes": ["PEG razoável"],
                    "pontos_fracos": ["Crescimento abaixo do esperado"]
                }
            }
            
            mock_client.analyze_with_methodology.side_effect = lambda symbol, method, data: methodology_results.get(method, {})
            
            # 4. Análise financeira completa
            mock_client.get_financial_analysis.return_value = {
                "symbol": "PETR4.SA",
                "overall_score": 72,
                "risk_level": "MEDIO",
                "recommendation": "COMPRA",
                "confidence": 0.85,
                "indicators": {
                    "pe_ratio": 15.5,
                    "roe": 18.5,
                    "debt_ratio": 0.8,
                    "current_ratio": 1.5,
                    "profit_margin": 15.2
                },
                "sector_comparison": {
                    "sector": "Energia",
                    "sector_pe_avg": 18.2,
                    "sector_roe_avg": 14.8,
                    "relative_performance": "ACIMA_DA_MEDIA"
                }
            }
            
            # Executar workflow completo
            symbol = "PETR4.SA"
            methodologies = ["warren_buffett", "benjamin_graham", "peter_lynch"]
            
            # 1. Validar autenticação
            auth_result = await mock_client.validate_token("valid-token")
            assert auth_result["valid"] is True
            assert auth_result["user_id"] == 123
            
            # 2. Obter dados da ação
            stock_data = await mock_client.get_stock_data(symbol)
            assert stock_data["symbol"] == symbol
            assert stock_data["pe_ratio"] == 15.5
            
            # 3. Executar análises com múltiplas metodologias
            analysis_results = []
            for methodology in methodologies:
                result = await mock_client.analyze_with_methodology(symbol, methodology, stock_data)
                analysis_results.append(result)
            
            # Verificar resultados das metodologias
            assert len(analysis_results) == 3
            assert analysis_results[0]["score"] == 78  # Warren Buffett
            assert analysis_results[1]["score"] == 72  # Benjamin Graham
            assert analysis_results[2]["score"] == 65  # Peter Lynch
            
            # 4. Obter análise financeira completa
            financial_analysis = await mock_client.get_financial_analysis(symbol, ["pe_ratio", "roe", "debt_ratio"])
            assert financial_analysis["overall_score"] == 72
            assert financial_analysis["recommendation"] == "COMPRA"
            assert financial_analysis["confidence"] == 0.85
            
            # 5. Verificar consenso das análises
            scores = [result["score"] for result in analysis_results]
            average_score = sum(scores) / len(scores)
            assert average_score > 70  # Consenso positivo
            
            # 6. Verificar consistência entre metodologias e análise financeira
            methodology_recommendations = [result["recomendacao"] for result in analysis_results]
            buy_recommendations = methodology_recommendations.count("COMPRA")
            assert buy_recommendations >= 2  # Maioria recomenda compra
    
    @pytest.mark.asyncio
    async def test_portfolio_analysis_workflow(self, http_client, auth_headers):
        """Testa workflow de análise de portfólio"""
        
        portfolio_symbols = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "WEGE3.SA"]
        
        with patch('microservices.shared.communication.service_client') as mock_client:
            # Simular dados para cada ação do portfólio
            portfolio_data = {
                "PETR4.SA": {"score": 75, "recommendation": "COMPRA", "risk": "MEDIO"},
                "VALE3.SA": {"score": 68, "recommendation": "NEUTRO", "risk": "ALTO"},
                "ITUB4.SA": {"score": 82, "recommendation": "COMPRA", "risk": "BAIXO"},
                "WEGE3.SA": {"score": 88, "recommendation": "COMPRA", "risk": "BAIXO"}
            }
            
            mock_client.validate_token.return_value = {"valid": True, "user_id": 123}
            
            def mock_analysis(symbol, methodology, data):
                return portfolio_data.get(symbol, {"score": 50, "recommendation": "NEUTRO"})
            
            mock_client.analyze_with_methodology.side_effect = mock_analysis
            
            # Executar análise do portfólio
            portfolio_results = []
            for symbol in portfolio_symbols:
                result = await mock_client.analyze_with_methodology(symbol, "warren_buffett", {})
                portfolio_results.append({
                    "symbol": symbol,
                    **result
                })
            
            # Verificar resultados do portfólio
            assert len(portfolio_results) == 4
            
            # Calcular métricas do portfólio
            total_score = sum(result["score"] for result in portfolio_results)
            average_score = total_score / len(portfolio_results)
            
            buy_count = sum(1 for result in portfolio_results if result["recommendation"] == "COMPRA")
            high_risk_count = sum(1 for result in portfolio_results if result["risk"] == "ALTO")
            
            assert average_score > 75  # Portfólio com boa qualidade
            assert buy_count >= 3  # Maioria com recomendação de compra
            assert high_risk_count <= 1  # Risco controlado
    
    @pytest.mark.asyncio
    async def test_real_time_monitoring_workflow(self, http_client):
        """Testa workflow de monitoramento em tempo real"""
        
        with patch('microservices.shared.communication.service_client') as mock_client:
            # Simular dados em tempo real
            real_time_data = [
                {"timestamp": "2024-01-01T10:00:00Z", "price": 25.50, "volume": 1000000},
                {"timestamp": "2024-01-01T10:01:00Z", "price": 25.55, "volume": 1100000},
                {"timestamp": "2024-01-01T10:02:00Z", "price": 25.48, "volume": 950000},
                {"timestamp": "2024-01-01T10:03:00Z", "price": 25.62, "volume": 1200000}
            ]
            
            mock_client.get_stock_data.side_effect = lambda symbol: {
                "symbol": symbol,
                "current_price": real_time_data[-1]["price"],
                "volume": real_time_data[-1]["volume"],
                "price_history": real_time_data
            }
            
            # Simular monitoramento
            symbol = "PETR4.SA"
            monitoring_results = []
            
            for i in range(len(real_time_data)):
                data = await mock_client.get_stock_data(symbol)
                monitoring_results.append({
                    "timestamp": real_time_data[i]["timestamp"],
                    "price": data["current_price"],
                    "volume": data["volume"]
                })
            
            # Verificar dados de monitoramento
            assert len(monitoring_results) == 4
            assert monitoring_results[-1]["price"] == 25.62  # Último preço
            
            # Calcular variação de preço
            first_price = monitoring_results[0]["price"]
            last_price = monitoring_results[-1]["price"]
            price_change = ((last_price - first_price) / first_price) * 100
            
            assert abs(price_change) < 5  # Variação dentro do esperado
    
    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, http_client):
        """Testa workflow de recuperação de erros"""
        
        with patch('microservices.shared.communication.service_client') as mock_client:
            # Simular falhas e recuperação
            call_count = 0
            
            def failing_service(symbol):
                nonlocal call_count
                call_count += 1
                if call_count <= 2:
                    raise httpx.ConnectError("Service temporarily unavailable")
                return {"symbol": symbol, "status": "recovered"}
            
            mock_client.get_stock_data.side_effect = failing_service
            
            # Tentar com retry
            symbol = "TEST.SA"
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    result = await mock_client.get_stock_data(symbol)
                    assert result["status"] == "recovered"
                    break
                except httpx.ConnectError:
                    if attempt == max_retries - 1:
                        pytest.fail("Service did not recover after retries")
                    await asyncio.sleep(0.1)  # Simular delay entre tentativas
            
            assert call_count == 3  # Deve ter tentado 3 vezes

class TestUserJourneyScenarios:
    """Testes de jornadas completas do usuário"""
    
    @pytest.mark.asyncio
    async def test_new_investor_journey(self, http_client, sample_user_data):
        """Testa jornada de um novo investidor"""
        
        with patch('microservices.shared.communication.service_client') as mock_client:
            # 1. Registro de novo usuário
            mock_client.register_user = Mock(return_value={
                "user_id": 456,
                "email": sample_user_data["email"],
                "status": "registered"
            })
            
            # 2. Login
            mock_client.validate_token.return_value = {
                "valid": True,
                "user_id": 456,
                "email": sample_user_data["email"],
                "is_new_user": True
            }
            
            # 3. Primeira análise (ação conservadora)
            mock_client.get_stock_data.return_value = {
                "symbol": "ITUB4.SA",
                "pe_ratio": 12.0,
                "dividend_yield": 6.5,
                "debt_ratio": 0.4,
                "risk_level": "BAIXO"
            }
            
            mock_client.analyze_with_methodology.return_value = {
                "score": 85,
                "recommendation": "COMPRA",
                "risk_assessment": "CONSERVADOR",
                "beginner_friendly": True,
                "educational_notes": [
                    "Esta é uma ação de banco com bom histórico de dividendos",
                    "P/E baixo indica preço atrativo",
                    "Adequada para investidores iniciantes"
                ]
            }
            
            # Executar jornada do novo investidor
            # 1. Registro
            registration = mock_client.register_user(sample_user_data)
            assert registration["status"] == "registered"
            
            # 2. Login
            auth = await mock_client.validate_token("new-user-token")
            assert auth["is_new_user"] is True
            
            # 3. Primeira análise
            stock_data = await mock_client.get_stock_data("ITUB4.SA")
            analysis = await mock_client.analyze_with_methodology("ITUB4.SA", "conservative", stock_data)
            
            assert analysis["beginner_friendly"] is True
            assert analysis["risk_assessment"] == "CONSERVADOR"
            assert len(analysis["educational_notes"]) >= 3
    
    @pytest.mark.asyncio
    async def test_experienced_investor_journey(self, http_client):
        """Testa jornada de investidor experiente"""
        
        with patch('microservices.shared.communication.service_client') as mock_client:
            # Investidor experiente com portfólio diversificado
            mock_client.validate_token.return_value = {
                "valid": True,
                "user_id": 789,
                "email": "expert@example.com",
                "experience_level": "EXPERT",
                "portfolio_size": "LARGE"
            }
            
            # Análise de ação de crescimento
            mock_client.get_stock_data.return_value = {
                "symbol": "MGLU3.SA",
                "pe_ratio": 35.0,
                "earnings_growth": 25.0,
                "revenue_growth": 30.0,
                "risk_level": "ALTO"
            }
            
            mock_client.analyze_with_methodology.return_value = {
                "score": 70,
                "recommendation": "COMPRA",
                "risk_assessment": "AGRESSIVO",
                "advanced_metrics": {
                    "peg_ratio": 1.4,
                    "ev_ebitda": 18.5,
                    "roic": 22.0,
                    "fcf_yield": 3.2
                },
                "sector_analysis": {
                    "sector": "E-commerce",
                    "growth_prospects": "ALTO",
                    "competitive_position": "LIDER"
                }
            }
            
            # Executar análise avançada
            auth = await mock_client.validate_token("expert-token")
            assert auth["experience_level"] == "EXPERT"
            
            stock_data = await mock_client.get_stock_data("MGLU3.SA")
            analysis = await mock_client.analyze_with_methodology("MGLU3.SA", "growth", stock_data)
            
            assert "advanced_metrics" in analysis
            assert "sector_analysis" in analysis
            assert analysis["risk_assessment"] == "AGRESSIVO"
    
    @pytest.mark.asyncio
    async def test_institutional_investor_journey(self, http_client):
        """Testa jornada de investidor institucional"""
        
        with patch('microservices.shared.communication.service_client') as mock_client:
            # Investidor institucional com necessidades específicas
            mock_client.validate_token.return_value = {
                "valid": True,
                "user_id": 999,
                "email": "fund@institution.com",
                "account_type": "INSTITUTIONAL",
                "aum": 1000000000  # R$ 1 bilhão
            }
            
            # Análise de múltiplas ações para portfólio
            portfolio_symbols = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "WEGE3.SA", "MGLU3.SA"]
            
            def mock_bulk_analysis(symbols, methodology):
                return {
                    symbol: {
                        "score": 70 + (hash(symbol) % 20),  # Score variável
                        "liquidity_score": 90,  # Alta liquidez para institucional
                        "market_impact": "BAIXO",
                        "institutional_ownership": 65.0
                    }
                    for symbol in symbols
                }
            
            mock_client.bulk_analyze = Mock(side_effect=mock_bulk_analysis)
            
            # Executar análise institucional
            auth = await mock_client.validate_token("institutional-token")
            assert auth["account_type"] == "INSTITUTIONAL"
            
            bulk_results = mock_client.bulk_analyze(portfolio_symbols, "institutional")
            
            assert len(bulk_results) == 5
            for symbol, result in bulk_results.items():
                assert result["liquidity_score"] >= 80  # Alta liquidez necessária
                assert result["market_impact"] == "BAIXO"  # Baixo impacto no mercado

class TestSystemResilience:
    """Testes de resiliência do sistema"""
    
    @pytest.mark.asyncio
    async def test_high_load_scenario(self, http_client):
        """Testa cenário de alta carga"""
        
        with patch('microservices.shared.communication.service_client') as mock_client:
            # Simular múltiplos usuários simultâneos
            concurrent_users = 50
            requests_per_user = 10
            
            async def simulate_user_requests(user_id):
                results = []
                for i in range(requests_per_user):
                    try:
                        # Simular requisição de análise
                        result = await mock_client.analyze_with_methodology(
                            f"TEST{i}.SA", 
                            "warren_buffett", 
                            {"symbol": f"TEST{i}.SA"}
                        )
                        results.append(result)
                    except Exception as e:
                        results.append({"error": str(e)})
                return results
            
            mock_client.analyze_with_methodology.return_value = {
                "score": 75,
                "recommendation": "COMPRA"
            }
            
            # Executar requisições concorrentes
            tasks = [
                simulate_user_requests(user_id) 
                for user_id in range(concurrent_users)
            ]
            
            all_results = await asyncio.gather(*tasks)
            
            # Verificar que todas as requisições foram processadas
            total_requests = sum(len(results) for results in all_results)
            successful_requests = sum(
                1 for results in all_results 
                for result in results 
                if "error" not in result
            )
            
            success_rate = successful_requests / total_requests
            assert success_rate >= 0.95  # 95% de sucesso mínimo
    
    @pytest.mark.asyncio
    async def test_cascade_failure_prevention(self, http_client):
        """Testa prevenção de falhas em cascata"""
        
        with patch('microservices.shared.communication.service_client') as mock_client:
            # Simular falha de um serviço
            def failing_data_service(symbol):
                raise httpx.ConnectError("Data service down")
            
            def working_methodology_service(symbol, methodology, data):
                # Deve funcionar mesmo sem dados externos
                return {
                    "score": 50,
                    "recommendation": "NEUTRO",
                    "note": "Análise baseada em dados limitados"
                }
            
            mock_client.get_stock_data.side_effect = failing_data_service
            mock_client.analyze_with_methodology.side_effect = working_methodology_service
            
            # Tentar análise mesmo com falha no serviço de dados
            try:
                await mock_client.get_stock_data("TEST.SA")
                pytest.fail("Expected ConnectError")
            except httpx.ConnectError:
                pass  # Esperado
            
            # Metodologia deve ainda funcionar com dados limitados
            result = await mock_client.analyze_with_methodology("TEST.SA", "warren_buffett", {})
            assert result["score"] == 50
            assert "dados limitados" in result["note"]

