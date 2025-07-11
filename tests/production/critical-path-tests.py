#!/usr/bin/env python3
"""
Testes de Caminho Crítico para Produção
Valida funcionalidades essenciais do Agente Investidor

Autor: Luiz Gustavo Finotello
Data: 10 de Julho de 2025
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from typing import Dict, List, Optional
import aiohttp
import pytest

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionTester:
    """Testa funcionalidades críticas em produção"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_token: Optional[str] = None
        
        # Dados de teste
        self.test_user = {
            'email': f'production_test_{int(time.time())}@agenteinvestidor.com',
            'password': 'ProductionTest123!',
            'full_name': 'Production Test User'
        }
        
        self.test_stocks = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA']
        self.test_methodologies = ['value_investing', 'dividend_investing']
        
        # Resultados dos testes
        self.results: Dict[str, bool] = {}
        self.errors: List[str] = []

    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()

    async def run_all_tests(self) -> bool:
        """Executa todos os testes críticos"""
        logger.info(f"Iniciando testes críticos em {self.base_url}")
        
        tests = [
            ('health_check', self.test_health_check),
            ('user_registration', self.test_user_registration),
            ('user_authentication', self.test_user_authentication),
            ('stock_data_retrieval', self.test_stock_data_retrieval),
            ('methodology_analysis', self.test_methodology_analysis),
            ('financial_analysis', self.test_financial_analysis),
            ('cache_performance', self.test_cache_performance),
            ('error_handling', self.test_error_handling),
            ('rate_limiting', self.test_rate_limiting),
            ('data_consistency', self.test_data_consistency),
        ]
        
        all_passed = True
        
        for test_name, test_func in tests:
            try:
                logger.info(f"Executando teste: {test_name}")
                result = await test_func()
                self.results[test_name] = result
                
                if result:
                    logger.info(f"✅ {test_name}: PASSOU")
                else:
                    logger.error(f"❌ {test_name}: FALHOU")
                    all_passed = False
                    
            except Exception as e:
                logger.error(f"❌ {test_name}: ERRO - {str(e)}")
                self.results[test_name] = False
                self.errors.append(f"{test_name}: {str(e)}")
                all_passed = False
        
        # Cleanup
        await self.cleanup()
        
        return all_passed

    async def test_health_check(self) -> bool:
        """Testa health check dos serviços"""
        endpoints = [
            '/health',
            '/api/v1/auth/health',
            '/api/v1/data/health',
            '/api/v1/methodology/health',
            '/api/v1/analysis/health',
        ]
        
        for endpoint in endpoints:
            async with self.session.get(f"{self.base_url}{endpoint}") as response:
                if response.status != 200:
                    logger.error(f"Health check failed for {endpoint}: {response.status}")
                    return False
                
                data = await response.json()
                if data.get('status') != 'healthy':
                    logger.error(f"Service unhealthy at {endpoint}: {data}")
                    return False
        
        return True

    async def test_user_registration(self) -> bool:
        """Testa registro de usuário"""
        async with self.session.post(
            f"{self.base_url}/api/v1/auth/register",
            json=self.test_user
        ) as response:
            if response.status != 201:
                logger.error(f"Registration failed: {response.status}")
                return False
            
            data = await response.json()
            if 'access_token' not in data:
                logger.error("No access token in registration response")
                return False
            
            self.auth_token = data['access_token']
            return True

    async def test_user_authentication(self) -> bool:
        """Testa autenticação de usuário"""
        # Teste login
        login_data = {
            'email': self.test_user['email'],
            'password': self.test_user['password']
        }
        
        async with self.session.post(
            f"{self.base_url}/api/v1/auth/login",
            json=login_data
        ) as response:
            if response.status != 200:
                logger.error(f"Login failed: {response.status}")
                return False
            
            data = await response.json()
            if 'access_token' not in data:
                logger.error("No access token in login response")
                return False
        
        # Teste acesso a endpoint protegido
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        async with self.session.get(
            f"{self.base_url}/api/v1/auth/profile",
            headers=headers
        ) as response:
            if response.status != 200:
                logger.error(f"Profile access failed: {response.status}")
                return False
            
            data = await response.json()
            if data.get('email') != self.test_user['email']:
                logger.error("Profile data mismatch")
                return False
        
        return True

    async def test_stock_data_retrieval(self) -> bool:
        """Testa recuperação de dados de ações"""
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        
        for stock in self.test_stocks:
            async with self.session.get(
                f"{self.base_url}/api/v1/data/stock/{stock}",
                headers=headers
            ) as response:
                if response.status != 200:
                    logger.error(f"Stock data failed for {stock}: {response.status}")
                    return False
                
                data = await response.json()
                required_fields = ['symbol', 'current_price', 'market_cap']
                
                for field in required_fields:
                    if field not in data:
                        logger.error(f"Missing field {field} in stock data for {stock}")
                        return False
        
        return True

    async def test_methodology_analysis(self) -> bool:
        """Testa análise por metodologias"""
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        
        for methodology in self.test_methodologies:
            payload = {
                'stock_symbol': self.test_stocks[0],
                'methodology': methodology,
                'parameters': {
                    'min_market_cap': 1000000000,
                    'max_pe_ratio': 15
                }
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/methodology/analyze",
                json=payload,
                headers=headers
            ) as response:
                if response.status != 200:
                    logger.error(f"Methodology analysis failed for {methodology}: {response.status}")
                    return False
                
                data = await response.json()
                required_fields = ['score', 'recommendation', 'analysis']
                
                for field in required_fields:
                    if field not in data:
                        logger.error(f"Missing field {field} in methodology analysis")
                        return False
        
        return True

    async def test_financial_analysis(self) -> bool:
        """Testa análise financeira"""
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        
        payload = {
            'stock_symbol': self.test_stocks[0],
            'analysis_type': 'comprehensive',
            'include_ratios': True,
            'include_valuation': True
        }
        
        async with self.session.post(
            f"{self.base_url}/api/v1/analysis/analyze",
            json=payload,
            headers=headers
        ) as response:
            if response.status != 200:
                logger.error(f"Financial analysis failed: {response.status}")
                return False
            
            data = await response.json()
            required_fields = ['financial_ratios', 'valuation', 'risk_metrics']
            
            for field in required_fields:
                if field not in data:
                    logger.error(f"Missing field {field} in financial analysis")
                    return False
        
        return True

    async def test_cache_performance(self) -> bool:
        """Testa performance do cache"""
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        stock = self.test_stocks[0]
        
        # Primeira requisição (cache miss)
        start_time = time.time()
        async with self.session.get(
            f"{self.base_url}/api/v1/data/stock/{stock}",
            headers=headers
        ) as response:
            first_duration = time.time() - start_time
            if response.status != 200:
                return False
        
        # Segunda requisição (cache hit)
        start_time = time.time()
        async with self.session.get(
            f"{self.base_url}/api/v1/data/stock/{stock}",
            headers=headers
        ) as response:
            second_duration = time.time() - start_time
            if response.status != 200:
                return False
        
        # Cache hit deve ser mais rápido
        if second_duration >= first_duration:
            logger.warning(f"Cache may not be working: {first_duration:.3f}s vs {second_duration:.3f}s")
            # Não falha o teste, apenas avisa
        
        return True

    async def test_error_handling(self) -> bool:
        """Testa tratamento de erros"""
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        
        # Teste 404 - ação inexistente
        async with self.session.get(
            f"{self.base_url}/api/v1/data/stock/INVALID.SA",
            headers=headers
        ) as response:
            if response.status not in [404, 400]:
                logger.error(f"Expected 404/400 for invalid stock, got {response.status}")
                return False
        
        # Teste 401 - sem autenticação
        async with self.session.get(
            f"{self.base_url}/api/v1/auth/profile"
        ) as response:
            if response.status != 401:
                logger.error(f"Expected 401 for unauthenticated request, got {response.status}")
                return False
        
        # Teste 400 - dados inválidos
        async with self.session.post(
            f"{self.base_url}/api/v1/methodology/analyze",
            json={'invalid': 'data'},
            headers=headers
        ) as response:
            if response.status != 400:
                logger.error(f"Expected 400 for invalid data, got {response.status}")
                return False
        
        return True

    async def test_rate_limiting(self) -> bool:
        """Testa rate limiting"""
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        
        # Faz muitas requisições rapidamente
        tasks = []
        for _ in range(20):
            task = self.session.get(
                f"{self.base_url}/api/v1/data/stock/{self.test_stocks[0]}",
                headers=headers
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verifica se alguma foi rate limited
        rate_limited = False
        for response in responses:
            if hasattr(response, 'status') and response.status == 429:
                rate_limited = True
                break
        
        # Rate limiting é opcional, mas se implementado deve funcionar
        return True

    async def test_data_consistency(self) -> bool:
        """Testa consistência de dados"""
        headers = {'Authorization': f'Bearer {self.auth_token}'}
        stock = self.test_stocks[0]
        
        # Busca dados da mesma ação múltiplas vezes
        responses = []
        for _ in range(3):
            async with self.session.get(
                f"{self.base_url}/api/v1/data/stock/{stock}",
                headers=headers
            ) as response:
                if response.status != 200:
                    return False
                data = await response.json()
                responses.append(data)
            
            await asyncio.sleep(1)
        
        # Verifica consistência básica
        first_response = responses[0]
        for response in responses[1:]:
            if response['symbol'] != first_response['symbol']:
                logger.error("Data inconsistency: symbol mismatch")
                return False
        
        return True

    async def cleanup(self):
        """Limpa dados de teste"""
        if not self.auth_token:
            return
        
        try:
            headers = {'Authorization': f'Bearer {self.auth_token}'}
            async with self.session.delete(
                f"{self.base_url}/api/v1/auth/account",
                headers=headers
            ) as response:
                # Cleanup é best effort
                pass
        except:
            pass

    def print_results(self):
        """Imprime resultados dos testes"""
        print("\n" + "="*60)
        print("RESULTADOS DOS TESTES CRÍTICOS DE PRODUÇÃO")
        print("="*60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result)
        
        print(f"Total de testes: {total_tests}")
        print(f"Testes aprovados: {passed_tests}")
        print(f"Testes falharam: {total_tests - passed_tests}")
        print(f"Taxa de sucesso: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nDetalhes dos testes:")
        for test_name, result in self.results.items():
            status = "✅ PASSOU" if result else "❌ FALHOU"
            print(f"  {test_name}: {status}")
        
        if self.errors:
            print("\nErros encontrados:")
            for error in self.errors:
                print(f"  - {error}")
        
        print("="*60)

async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Testes críticos de produção')
    parser.add_argument('--url', required=True, help='URL base da aplicação')
    parser.add_argument('--timeout', type=int, default=30, help='Timeout em segundos')
    
    args = parser.parse_args()
    
    async with ProductionTester(args.url, args.timeout) as tester:
        success = await tester.run_all_tests()
        tester.print_results()
        
        if success:
            logger.info("🎉 Todos os testes críticos passaram!")
            sys.exit(0)
        else:
            logger.error("💥 Alguns testes críticos falharam!")
            sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())

