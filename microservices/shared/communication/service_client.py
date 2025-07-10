"""
Cliente de Comunicação entre Serviços
Responsável por comunicação HTTP síncrona com circuit breaker e retry
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class ServiceConfig:
    name: str
    base_url: str
    timeout: float = 30.0
    retries: int = 3
    retry_delay: float = 1.0
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: float = 60.0

@dataclass
class CircuitBreakerState:
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    next_attempt_time: Optional[datetime] = None

class ServiceClient:
    """Cliente para comunicação entre microserviços"""
    
    def __init__(self):
        self.services: Dict[str, ServiceConfig] = {}
        self.circuit_breakers: Dict[str, CircuitBreakerState] = {}
        self.client = httpx.AsyncClient()
        
        # Configurar serviços conhecidos
        self._setup_default_services()
    
    def _setup_default_services(self):
        """Configura serviços padrão"""
        self.register_service(ServiceConfig(
            name="auth-service",
            base_url="http://auth-service:8001",
            timeout=10.0,
            retries=2
        ))
        
        self.register_service(ServiceConfig(
            name="data-service", 
            base_url="http://data-service:8002",
            timeout=15.0,
            retries=3
        ))
        
        self.register_service(ServiceConfig(
            name="methodology-service",
            base_url="http://methodology-service:8003",
            timeout=20.0,
            retries=2
        ))
        
        self.register_service(ServiceConfig(
            name="analysis-service",
            base_url="http://analysis-service:8004", 
            timeout=25.0,
            retries=2
        ))
    
    def register_service(self, config: ServiceConfig):
        """Registra um novo serviço"""
        self.services[config.name] = config
        self.circuit_breakers[config.name] = CircuitBreakerState()
        logger.info(f"Serviço registrado: {config.name} -> {config.base_url}")
    
    def _get_circuit_breaker(self, service_name: str) -> CircuitBreakerState:
        """Obtém o circuit breaker para um serviço"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreakerState()
        return self.circuit_breakers[service_name]
    
    def _can_execute(self, service_name: str) -> bool:
        """Verifica se pode executar requisição baseado no circuit breaker"""
        cb = self._get_circuit_breaker(service_name)
        config = self.services.get(service_name)
        
        if not config:
            return False
        
        now = datetime.utcnow()
        
        if cb.state == CircuitState.CLOSED:
            return True
        
        elif cb.state == CircuitState.OPEN:
            if cb.next_attempt_time and now >= cb.next_attempt_time:
                cb.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker {service_name}: OPEN -> HALF_OPEN")
                return True
            return False
        
        elif cb.state == CircuitState.HALF_OPEN:
            return True
        
        return False
    
    def _record_success(self, service_name: str):
        """Registra sucesso na comunicação"""
        cb = self._get_circuit_breaker(service_name)
        
        if cb.state == CircuitState.HALF_OPEN:
            cb.state = CircuitState.CLOSED
            cb.failure_count = 0
            logger.info(f"Circuit breaker {service_name}: HALF_OPEN -> CLOSED")
        
        cb.failure_count = max(0, cb.failure_count - 1)
    
    def _record_failure(self, service_name: str):
        """Registra falha na comunicação"""
        cb = self._get_circuit_breaker(service_name)
        config = self.services.get(service_name)
        
        if not config:
            return
        
        cb.failure_count += 1
        cb.last_failure_time = datetime.utcnow()
        
        if cb.failure_count >= config.circuit_breaker_threshold:
            cb.state = CircuitState.OPEN
            cb.next_attempt_time = datetime.utcnow() + timedelta(seconds=config.circuit_breaker_timeout)
            logger.warning(f"Circuit breaker {service_name}: CLOSED -> OPEN (failures: {cb.failure_count})")
    
    async def _make_request(
        self,
        service_name: str,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """Faz requisição HTTP com retry e circuit breaker"""
        
        if not self._can_execute(service_name):
            raise Exception(f"Circuit breaker OPEN para {service_name}")
        
        config = self.services.get(service_name)
        if not config:
            raise Exception(f"Serviço {service_name} não registrado")
        
        url = f"{config.base_url}{endpoint}"
        request_timeout = timeout or config.timeout
        
        # Headers padrão
        request_headers = {
            "Content-Type": "application/json",
            "User-Agent": "ServiceClient/1.0"
        }
        if headers:
            request_headers.update(headers)
        
        last_exception = None
        
        for attempt in range(config.retries + 1):
            try:
                logger.info(f"Requisição {method} {url} (tentativa {attempt + 1})")
                
                if method.upper() == "GET":
                    response = await self.client.get(
                        url,
                        headers=request_headers,
                        timeout=request_timeout
                    )
                elif method.upper() == "POST":
                    response = await self.client.post(
                        url,
                        json=data,
                        headers=request_headers,
                        timeout=request_timeout
                    )
                elif method.upper() == "PUT":
                    response = await self.client.put(
                        url,
                        json=data,
                        headers=request_headers,
                        timeout=request_timeout
                    )
                elif method.upper() == "DELETE":
                    response = await self.client.delete(
                        url,
                        headers=request_headers,
                        timeout=request_timeout
                    )
                else:
                    raise Exception(f"Método HTTP {method} não suportado")
                
                # Verificar status da resposta
                if response.status_code >= 400:
                    raise httpx.HTTPStatusError(
                        f"HTTP {response.status_code}",
                        request=response.request,
                        response=response
                    )
                
                # Sucesso
                self._record_success(service_name)
                
                try:
                    return response.json()
                except:
                    return {"status": "success", "data": response.text}
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Falha na requisição {method} {url}: {e}")
                
                if attempt < config.retries:
                    await asyncio.sleep(config.retry_delay * (attempt + 1))
                else:
                    self._record_failure(service_name)
        
        raise last_exception
    
    # Métodos de conveniência
    async def get(self, service_name: str, endpoint: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """GET request"""
        return await self._make_request(service_name, "GET", endpoint, headers=headers)
    
    async def post(self, service_name: str, endpoint: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """POST request"""
        return await self._make_request(service_name, "POST", endpoint, data=data, headers=headers)
    
    async def put(self, service_name: str, endpoint: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """PUT request"""
        return await self._make_request(service_name, "PUT", endpoint, data=data, headers=headers)
    
    async def delete(self, service_name: str, endpoint: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """DELETE request"""
        return await self._make_request(service_name, "DELETE", endpoint, headers=headers)
    
    # Métodos específicos para serviços
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Valida token no serviço de autenticação"""
        headers = {"Authorization": f"Bearer {token}"}
        return await self.get("auth-service", "/validate", headers=headers)
    
    async def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Obtém dados de ação do serviço de dados"""
        return await self.get("data-service", f"/stock/{symbol}")
    
    async def analyze_with_methodology(self, symbol: str, methodology: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa ação com metodologia específica"""
        payload = {
            "symbol": symbol,
            "methodology": methodology,
            "data": data
        }
        return await self.post("methodology-service", "/analyze", data=payload)
    
    async def get_financial_analysis(self, symbol: str, indicators: List[str]) -> Dict[str, Any]:
        """Obtém análise financeira completa"""
        payload = {
            "symbol": symbol,
            "indicators": indicators
        }
        return await self.post("analysis-service", "/analyze", data=payload)
    
    async def health_check(self, service_name: str) -> Dict[str, Any]:
        """Verifica saúde de um serviço"""
        return await self.get(service_name, "/health")
    
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Verifica saúde de todos os serviços"""
        results = {}
        
        for service_name in self.services.keys():
            try:
                result = await self.health_check(service_name)
                results[service_name] = {
                    "status": "healthy",
                    "response": result,
                    "circuit_breaker": self.circuit_breakers[service_name].state.value
                }
            except Exception as e:
                results[service_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "circuit_breaker": self.circuit_breakers[service_name].state.value
                }
        
        return results
    
    async def close(self):
        """Fecha cliente HTTP"""
        await self.client.aclose()

# Instância global do cliente
service_client = ServiceClient()

# Funções de conveniência
async def call_service(service_name: str, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Função de conveniência para chamar serviços"""
    return await service_client._make_request(service_name, method, endpoint, data, headers)

async def validate_user_token(token: str) -> Dict[str, Any]:
    """Valida token de usuário"""
    return await service_client.validate_token(token)

async def get_stock_data(symbol: str) -> Dict[str, Any]:
    """Obtém dados de ação"""
    return await service_client.get_stock_data(symbol)

async def analyze_stock(symbol: str, methodology: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Analisa ação com metodologia"""
    return await service_client.analyze_with_methodology(symbol, methodology, data)

