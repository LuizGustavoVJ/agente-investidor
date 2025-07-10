"""
Gerenciador de Cache Redis Avançado
Implementa estratégias de cache hierárquico, invalidação inteligente e cache warming
"""

import os
import json
import redis
import hashlib
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import structlog

logger = structlog.get_logger()

class CacheLevel(Enum):
    """Níveis de cache hierárquico"""
    L1_MEMORY = "l1_memory"      # Cache em memória (mais rápido)
    L2_REDIS = "l2_redis"        # Cache Redis (persistente)
    L3_DATABASE = "l3_database"  # Cache no banco (backup)

@dataclass
class CacheConfig:
    """Configuração de cache"""
    ttl: int = 3600  # TTL padrão em segundos
    level: CacheLevel = CacheLevel.L2_REDIS
    auto_refresh: bool = False
    refresh_threshold: float = 0.8  # Refresh quando 80% do TTL passou
    compression: bool = True
    serialization: str = "json"  # json, pickle, msgpack

class RedisManager:
    """Gerenciador avançado de cache Redis"""
    
    def __init__(self, host: str = None, port: int = None, db: int = 0):
        self.host = host or os.getenv("REDIS_HOST", "redis")
        self.port = port or int(os.getenv("REDIS_PORT", "6379"))
        self.db = db
        
        # Conexões Redis por database
        self.connections = {}
        
        # Cache em memória (L1)
        self.memory_cache = {}
        self.memory_cache_ttl = {}
        
        # Configurações padrão
        self.default_config = CacheConfig()
        
        # Estatísticas
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "invalidations": 0
        }
    
    def get_connection(self, db: int = None) -> redis.Redis:
        """Obter conexão Redis para database específico"""
        db = db or self.db
        
        if db not in self.connections:
            self.connections[db] = redis.Redis(
                host=self.host,
                port=self.port,
                db=db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
        
        return self.connections[db]
    
    def _generate_key(self, namespace: str, key: str, params: Dict = None) -> str:
        """Gerar chave de cache com namespace e parâmetros"""
        if params:
            # Criar hash dos parâmetros para chave única
            params_str = json.dumps(params, sort_keys=True)
            params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
            return f"{namespace}:{key}:{params_hash}"
        return f"{namespace}:{key}"
    
    def _serialize_value(self, value: Any, config: CacheConfig) -> str:
        """Serializar valor para cache"""
        if config.serialization == "json":
            return json.dumps(value, default=str)
        elif config.serialization == "pickle":
            import pickle
            import base64
            return base64.b64encode(pickle.dumps(value)).decode()
        else:
            return str(value)
    
    def _deserialize_value(self, value: str, config: CacheConfig) -> Any:
        """Deserializar valor do cache"""
        if config.serialization == "json":
            return json.loads(value)
        elif config.serialization == "pickle":
            import pickle
            import base64
            return pickle.loads(base64.b64decode(value.encode()))
        else:
            return value
    
    def _compress_value(self, value: str) -> str:
        """Comprimir valor para economizar espaço"""
        import gzip
        import base64
        compressed = gzip.compress(value.encode())
        return base64.b64encode(compressed).decode()
    
    def _decompress_value(self, value: str) -> str:
        """Descomprimir valor"""
        import gzip
        import base64
        compressed = base64.b64decode(value.encode())
        return gzip.decompress(compressed).decode()
    
    def set(self, namespace: str, key: str, value: Any, 
            config: CacheConfig = None, params: Dict = None) -> bool:
        """Definir valor no cache"""
        try:
            config = config or self.default_config
            cache_key = self._generate_key(namespace, key, params)
            
            # Serializar valor
            serialized_value = self._serialize_value(value, config)
            
            # Comprimir se necessário
            if config.compression and len(serialized_value) > 1024:  # Comprimir se > 1KB
                serialized_value = self._compress_value(serialized_value)
                cache_key += ":compressed"
            
            # Metadados
            metadata = {
                "created_at": datetime.utcnow().isoformat(),
                "ttl": config.ttl,
                "level": config.level.value,
                "auto_refresh": config.auto_refresh,
                "compression": config.compression,
                "serialization": config.serialization
            }
            
            # Cache L1 (memória)
            if config.level == CacheLevel.L1_MEMORY:
                self.memory_cache[cache_key] = {
                    "value": value,  # Valor original sem serialização
                    "metadata": metadata
                }
                self.memory_cache_ttl[cache_key] = datetime.utcnow() + timedelta(seconds=config.ttl)
                self.stats["sets"] += 1
                return True
            
            # Cache L2 (Redis)
            redis_conn = self.get_connection()
            
            # Salvar valor e metadados
            pipe = redis_conn.pipeline()
            pipe.hset(cache_key, "value", serialized_value)
            pipe.hset(cache_key, "metadata", json.dumps(metadata))
            pipe.expire(cache_key, config.ttl)
            pipe.execute()
            
            self.stats["sets"] += 1
            logger.debug("Cache set", key=cache_key, ttl=config.ttl)
            return True
            
        except Exception as e:
            logger.error("Cache set failed", key=cache_key, error=str(e))
            return False
    
    def get(self, namespace: str, key: str, params: Dict = None, 
            default: Any = None) -> Any:
        """Obter valor do cache"""
        try:
            cache_key = self._generate_key(namespace, key, params)
            
            # Tentar cache L1 primeiro
            if cache_key in self.memory_cache:
                # Verificar TTL
                if cache_key in self.memory_cache_ttl:
                    if datetime.utcnow() > self.memory_cache_ttl[cache_key]:
                        # Expirado
                        del self.memory_cache[cache_key]
                        del self.memory_cache_ttl[cache_key]
                    else:
                        self.stats["hits"] += 1
                        return self.memory_cache[cache_key]["value"]
            
            # Tentar cache L2 (Redis)
            redis_conn = self.get_connection()
            
            # Verificar se existe
            if not redis_conn.exists(cache_key) and not redis_conn.exists(cache_key + ":compressed"):
                self.stats["misses"] += 1
                return default
            
            # Determinar se está comprimido
            compressed = redis_conn.exists(cache_key + ":compressed")
            actual_key = cache_key + ":compressed" if compressed else cache_key
            
            # Obter valor e metadados
            cached_data = redis_conn.hmget(actual_key, "value", "metadata")
            
            if not cached_data[0]:
                self.stats["misses"] += 1
                return default
            
            value = cached_data[0]
            metadata = json.loads(cached_data[1]) if cached_data[1] else {}
            
            # Descomprimir se necessário
            if compressed:
                value = self._decompress_value(value)
            
            # Deserializar
            config = CacheConfig(
                serialization=metadata.get("serialization", "json")
            )
            deserialized_value = self._deserialize_value(value, config)
            
            # Verificar se precisa de refresh automático
            if metadata.get("auto_refresh", False):
                created_at = datetime.fromisoformat(metadata["created_at"])
                ttl = metadata.get("ttl", 3600)
                refresh_threshold = metadata.get("refresh_threshold", 0.8)
                
                elapsed = (datetime.utcnow() - created_at).total_seconds()
                if elapsed > (ttl * refresh_threshold):
                    # Agendar refresh (implementar com Kafka se necessário)
                    logger.info("Cache refresh needed", key=cache_key)
            
            self.stats["hits"] += 1
            logger.debug("Cache hit", key=cache_key)
            return deserialized_value
            
        except Exception as e:
            logger.error("Cache get failed", key=cache_key, error=str(e))
            self.stats["misses"] += 1
            return default
    
    def delete(self, namespace: str, key: str, params: Dict = None) -> bool:
        """Deletar valor do cache"""
        try:
            cache_key = self._generate_key(namespace, key, params)
            
            # Deletar do cache L1
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]
                if cache_key in self.memory_cache_ttl:
                    del self.memory_cache_ttl[cache_key]
            
            # Deletar do Redis
            redis_conn = self.get_connection()
            deleted = redis_conn.delete(cache_key, cache_key + ":compressed")
            
            self.stats["deletes"] += 1
            logger.debug("Cache delete", key=cache_key, deleted=deleted)
            return deleted > 0
            
        except Exception as e:
            logger.error("Cache delete failed", key=cache_key, error=str(e))
            return False
    
    def invalidate_pattern(self, namespace: str, pattern: str = "*") -> int:
        """Invalidar cache por padrão"""
        try:
            redis_conn = self.get_connection()
            full_pattern = f"{namespace}:{pattern}"
            
            keys = redis_conn.keys(full_pattern)
            if keys:
                deleted = redis_conn.delete(*keys)
                self.stats["invalidations"] += deleted
                logger.info("Cache pattern invalidated", pattern=full_pattern, deleted=deleted)
                return deleted
            return 0
            
        except Exception as e:
            logger.error("Cache pattern invalidation failed", pattern=pattern, error=str(e))
            return 0
    
    def warm_cache(self, namespace: str, key: str, value_generator: Callable, 
                   config: CacheConfig = None, params: Dict = None) -> bool:
        """Aquecer cache com valor gerado"""
        try:
            # Verificar se já existe
            if self.get(namespace, key, params) is not None:
                return True  # Já existe
            
            # Gerar valor
            value = value_generator()
            
            # Salvar no cache
            return self.set(namespace, key, value, config, params)
            
        except Exception as e:
            logger.error("Cache warming failed", namespace=namespace, key=key, error=str(e))
            return False
    
    def get_or_set(self, namespace: str, key: str, value_generator: Callable,
                   config: CacheConfig = None, params: Dict = None) -> Any:
        """Obter do cache ou definir se não existir"""
        # Tentar obter do cache
        value = self.get(namespace, key, params)
        
        if value is not None:
            return value
        
        # Gerar e salvar valor
        try:
            value = value_generator()
            self.set(namespace, key, value, config, params)
            return value
        except Exception as e:
            logger.error("Cache get_or_set failed", namespace=namespace, key=key, error=str(e))
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas do cache"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.stats,
            "hit_rate": round(hit_rate, 2),
            "total_requests": total_requests,
            "memory_cache_size": len(self.memory_cache)
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Verificar saúde do cache"""
        try:
            redis_conn = self.get_connection()
            redis_conn.ping()
            
            info = redis_conn.info()
            
            return {
                "status": "healthy",
                "redis_version": info.get("redis_version"),
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "stats": self.get_stats()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "stats": self.get_stats()
            }

# Singleton global
redis_manager = RedisManager()

# Decorador para cache automático
def cached(namespace: str, key_func: Callable = None, ttl: int = 3600, 
           auto_refresh: bool = False):
    """Decorador para cache automático de funções"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Gerar chave baseada nos argumentos
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
            
            config = CacheConfig(ttl=ttl, auto_refresh=auto_refresh)
            
            return redis_manager.get_or_set(
                namespace=namespace,
                key=cache_key,
                value_generator=lambda: func(*args, **kwargs),
                config=config
            )
        return wrapper
    return decorator

