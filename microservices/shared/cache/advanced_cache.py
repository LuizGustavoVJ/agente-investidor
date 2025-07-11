"""
Cache Avançado Hierárquico para Agente Investidor
Implementa cache L1 (memória) + L2 (Redis) com compressão e auto-refresh

Autor: Luiz Gustavo Finotello
Data: 10 de Julho de 2025
"""

import asyncio
import json
import logging
import pickle
import time
import zlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, Gauge
import threading
from concurrent.futures import ThreadPoolExecutor

# Métricas Prometheus
cache_hits = Counter('cache_hits_total', 'Total cache hits', ['level', 'key_type'])
cache_misses = Counter('cache_misses_total', 'Total cache misses', ['level', 'key_type'])
cache_operations = Histogram('cache_operation_duration_seconds', 'Cache operation duration', ['operation', 'level'])
cache_size = Gauge('cache_size_bytes', 'Cache size in bytes', ['level'])
cache_items = Gauge('cache_items_total', 'Total items in cache', ['level'])

logger = logging.getLogger(__name__)

class CacheLevel(Enum):
    L1 = "l1"  # Memória local
    L2 = "l2"  # Redis distribuído

class SerializationMethod(Enum):
    JSON = "json"
    PICKLE = "pickle"
    MSGPACK = "msgpack"

@dataclass
class CacheEntry:
    """Entrada do cache com metadados"""
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    size_bytes: int = 0
    key_type: str = "unknown"
    compression_ratio: float = 1.0

class CacheStats:
    """Estatísticas do cache"""
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.size_bytes = 0
        self.item_count = 0
        self.hit_ratio = 0.0

class AdvancedCache:
    """
    Cache hierárquico avançado com:
    - L1: Cache em memória (rápido, limitado)
    - L2: Cache Redis (distribuído, persistente)
    - Compressão automática
    - Auto-refresh inteligente
    - Métricas detalhadas
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        l1_max_size: int = 1000,  # Máximo de itens em L1
        l1_max_memory: int = 100 * 1024 * 1024,  # 100MB
        default_ttl: int = 3600,  # 1 hora
        compression_threshold: int = 1024,  # Comprimir se > 1KB
        auto_refresh_threshold: float = 0.8,  # Refresh quando 80% do TTL
        enable_metrics: bool = True
    ):
        self.redis_url = redis_url
        self.l1_max_size = l1_max_size
        self.l1_max_memory = l1_max_memory
        self.default_ttl = default_ttl
        self.compression_threshold = compression_threshold
        self.auto_refresh_threshold = auto_refresh_threshold
        self.enable_metrics = enable_metrics
        
        # L1 Cache (memória)
        self.l1_cache: Dict[str, CacheEntry] = {}
        self.l1_lock = threading.RLock()
        self.l1_stats = CacheStats()
        
        # L2 Cache (Redis)
        self.redis_client: Optional[redis.Redis] = None
        self.l2_stats = CacheStats()
        
        # Auto-refresh
        self.refresh_callbacks: Dict[str, callable] = {}
        self.refresh_executor = ThreadPoolExecutor(max_workers=4)
        self.refresh_tasks: Dict[str, asyncio.Task] = {}
        
        # Configurações
        self.serialization_method = SerializationMethod.PICKLE
        
        logger.info(f"AdvancedCache initialized with L1_max_size={l1_max_size}, L1_max_memory={l1_max_memory}MB")

    async def initialize(self):
        """Inicializa conexão Redis"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=False)
            await self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None

    async def close(self):
        """Fecha conexões e limpa recursos"""
        if self.redis_client:
            await self.redis_client.close()
        
        # Cancela tasks de refresh
        for task in self.refresh_tasks.values():
            task.cancel()
        
        self.refresh_executor.shutdown(wait=True)

    def _serialize(self, value: Any) -> Tuple[bytes, SerializationMethod]:
        """Serializa valor para bytes"""
        if self.serialization_method == SerializationMethod.JSON:
            try:
                return json.dumps(value).encode('utf-8'), SerializationMethod.JSON
            except (TypeError, ValueError):
                # Fallback para pickle se JSON falhar
                return pickle.dumps(value), SerializationMethod.PICKLE
        else:
            return pickle.dumps(value), SerializationMethod.PICKLE

    def _deserialize(self, data: bytes, method: SerializationMethod) -> Any:
        """Deserializa bytes para valor"""
        if method == SerializationMethod.JSON:
            return json.loads(data.decode('utf-8'))
        else:
            return pickle.loads(data)

    def _compress(self, data: bytes) -> Tuple[bytes, bool]:
        """Comprime dados se necessário"""
        if len(data) > self.compression_threshold:
            compressed = zlib.compress(data)
            if len(compressed) < len(data) * 0.9:  # Só comprime se reduzir 10%+
                return compressed, True
        return data, False

    def _decompress(self, data: bytes, is_compressed: bool) -> bytes:
        """Descomprime dados se necessário"""
        if is_compressed:
            return zlib.decompress(data)
        return data

    def _generate_key_hash(self, key: str) -> str:
        """Gera hash da chave para evitar problemas com caracteres especiais"""
        return hashlib.sha256(key.encode('utf-8')).hexdigest()[:16]

    def _evict_l1_if_needed(self):
        """Remove itens do L1 se necessário (LRU)"""
        with self.l1_lock:
            # Verifica limite de itens
            while len(self.l1_cache) >= self.l1_max_size:
                self._evict_lru_l1()
            
            # Verifica limite de memória
            current_memory = sum(entry.size_bytes for entry in self.l1_cache.values())
            while current_memory > self.l1_max_memory and self.l1_cache:
                evicted_entry = self._evict_lru_l1()
                if evicted_entry:
                    current_memory -= evicted_entry.size_bytes

    def _evict_lru_l1(self) -> Optional[CacheEntry]:
        """Remove item menos recentemente usado do L1"""
        if not self.l1_cache:
            return None
        
        # Encontra item menos recentemente acessado
        lru_key = min(
            self.l1_cache.keys(),
            key=lambda k: self.l1_cache[k].last_accessed or self.l1_cache[k].created_at
        )
        
        evicted_entry = self.l1_cache.pop(lru_key)
        self.l1_stats.evictions += 1
        
        if self.enable_metrics:
            cache_items.labels(level="l1").dec()
            cache_size.labels(level="l1").dec(evicted_entry.size_bytes)
        
        logger.debug(f"Evicted L1 key: {lru_key}")
        return evicted_entry

    async def get(self, key: str, default: Any = None) -> Any:
        """
        Busca valor no cache (L1 -> L2)
        """
        start_time = time.time()
        
        try:
            # Tenta L1 primeiro
            l1_value = await self._get_l1(key)
            if l1_value is not None:
                if self.enable_metrics:
                    cache_hits.labels(level="l1", key_type=self._get_key_type(key)).inc()
                    cache_operations.labels(operation="get", level="l1").observe(time.time() - start_time)
                
                # Verifica se precisa de auto-refresh
                await self._check_auto_refresh(key, l1_value)
                return l1_value
            
            # Tenta L2 (Redis)
            l2_value = await self._get_l2(key)
            if l2_value is not None:
                if self.enable_metrics:
                    cache_hits.labels(level="l2", key_type=self._get_key_type(key)).inc()
                    cache_operations.labels(operation="get", level="l2").observe(time.time() - start_time)
                
                # Promove para L1
                await self._set_l1(key, l2_value)
                
                # Verifica se precisa de auto-refresh
                await self._check_auto_refresh(key, l2_value)
                return l2_value
            
            # Cache miss
            if self.enable_metrics:
                cache_misses.labels(level="l2", key_type=self._get_key_type(key)).inc()
            
            return default
            
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return default

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        key_type: str = "unknown",
        refresh_callback: Optional[callable] = None
    ) -> bool:
        """
        Define valor no cache (L1 + L2)
        """
        start_time = time.time()
        ttl = ttl or self.default_ttl
        
        try:
            # Define em L1
            await self._set_l1(key, value, ttl, key_type)
            
            # Define em L2 (Redis)
            await self._set_l2(key, value, ttl, key_type)
            
            # Registra callback de refresh se fornecido
            if refresh_callback:
                self.refresh_callbacks[key] = refresh_callback
            
            if self.enable_metrics:
                cache_operations.labels(operation="set", level="both").observe(time.time() - start_time)
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False

    async def _get_l1(self, key: str) -> Any:
        """Busca valor no L1 (memória)"""
        with self.l1_lock:
            entry = self.l1_cache.get(key)
            if entry is None:
                return None
            
            # Verifica expiração
            if entry.expires_at and datetime.now() > entry.expires_at:
                del self.l1_cache[key]
                self.l1_stats.evictions += 1
                if self.enable_metrics:
                    cache_items.labels(level="l1").dec()
                    cache_size.labels(level="l1").dec(entry.size_bytes)
                return None
            
            # Atualiza estatísticas de acesso
            entry.access_count += 1
            entry.last_accessed = datetime.now()
            self.l1_stats.hits += 1
            
            return entry.value

    async def _set_l1(self, key: str, value: Any, ttl: int = None, key_type: str = "unknown"):
        """Define valor no L1 (memória)"""
        ttl = ttl or self.default_ttl
        
        with self.l1_lock:
            # Remove entrada existente se houver
            if key in self.l1_cache:
                old_entry = self.l1_cache[key]
                if self.enable_metrics:
                    cache_size.labels(level="l1").dec(old_entry.size_bytes)
            
            # Calcula tamanho aproximado
            try:
                size_bytes = len(pickle.dumps(value))
            except:
                size_bytes = 1024  # Estimativa padrão
            
            # Cria nova entrada
            entry = CacheEntry(
                value=value,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(seconds=ttl),
                size_bytes=size_bytes,
                key_type=key_type,
                last_accessed=datetime.now()
            )
            
            self.l1_cache[key] = entry
            
            # Atualiza métricas
            if self.enable_metrics:
                cache_items.labels(level="l1").inc()
                cache_size.labels(level="l1").inc(size_bytes)
            
            # Verifica se precisa fazer eviction
            self._evict_l1_if_needed()

    async def _get_l2(self, key: str) -> Any:
        """Busca valor no L2 (Redis)"""
        if not self.redis_client:
            return None
        
        try:
            # Busca metadados e dados
            key_hash = self._generate_key_hash(key)
            meta_key = f"meta:{key_hash}"
            data_key = f"data:{key_hash}"
            
            meta_data = await self.redis_client.get(meta_key)
            if not meta_data:
                return None
            
            metadata = json.loads(meta_data)
            
            # Verifica expiração
            if metadata.get('expires_at'):
                expires_at = datetime.fromisoformat(metadata['expires_at'])
                if datetime.now() > expires_at:
                    await self.redis_client.delete(meta_key, data_key)
                    return None
            
            # Busca dados
            data = await self.redis_client.get(data_key)
            if not data:
                return None
            
            # Descomprime se necessário
            is_compressed = metadata.get('is_compressed', False)
            data = self._decompress(data, is_compressed)
            
            # Deserializa
            serialization_method = SerializationMethod(metadata.get('serialization_method', 'pickle'))
            value = self._deserialize(data, serialization_method)
            
            # Atualiza estatísticas de acesso
            metadata['access_count'] = metadata.get('access_count', 0) + 1
            metadata['last_accessed'] = datetime.now().isoformat()
            await self.redis_client.set(meta_key, json.dumps(metadata))
            
            self.l2_stats.hits += 1
            return value
            
        except Exception as e:
            logger.error(f"Error getting L2 cache key {key}: {e}")
            return None

    async def _set_l2(self, key: str, value: Any, ttl: int = None, key_type: str = "unknown"):
        """Define valor no L2 (Redis)"""
        if not self.redis_client:
            return
        
        ttl = ttl or self.default_ttl
        
        try:
            # Serializa valor
            data, serialization_method = self._serialize(value)
            
            # Comprime se necessário
            compressed_data, is_compressed = self._compress(data)
            compression_ratio = len(compressed_data) / len(data) if data else 1.0
            
            # Prepara metadados
            metadata = {
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(seconds=ttl)).isoformat(),
                'key_type': key_type,
                'serialization_method': serialization_method.value,
                'is_compressed': is_compressed,
                'compression_ratio': compression_ratio,
                'size_bytes': len(compressed_data),
                'access_count': 0
            }
            
            # Salva no Redis
            key_hash = self._generate_key_hash(key)
            meta_key = f"meta:{key_hash}"
            data_key = f"data:{key_hash}"
            
            pipe = self.redis_client.pipeline()
            pipe.set(meta_key, json.dumps(metadata), ex=ttl)
            pipe.set(data_key, compressed_data, ex=ttl)
            await pipe.execute()
            
            # Atualiza métricas
            if self.enable_metrics:
                cache_items.labels(level="l2").inc()
                cache_size.labels(level="l2").inc(len(compressed_data))
            
        except Exception as e:
            logger.error(f"Error setting L2 cache key {key}: {e}")

    async def delete(self, key: str) -> bool:
        """Remove chave do cache (L1 + L2)"""
        try:
            # Remove do L1
            with self.l1_lock:
                if key in self.l1_cache:
                    entry = self.l1_cache.pop(key)
                    if self.enable_metrics:
                        cache_items.labels(level="l1").dec()
                        cache_size.labels(level="l1").dec(entry.size_bytes)
            
            # Remove do L2
            if self.redis_client:
                key_hash = self._generate_key_hash(key)
                meta_key = f"meta:{key_hash}"
                data_key = f"data:{key_hash}"
                await self.redis_client.delete(meta_key, data_key)
            
            # Remove callback de refresh
            self.refresh_callbacks.pop(key, None)
            
            # Cancela task de refresh se existir
            if key in self.refresh_tasks:
                self.refresh_tasks[key].cancel()
                del self.refresh_tasks[key]
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False

    async def clear(self, pattern: str = "*") -> int:
        """Limpa cache baseado em padrão"""
        cleared_count = 0
        
        try:
            # Limpa L1
            with self.l1_lock:
                keys_to_remove = []
                for key in self.l1_cache.keys():
                    if pattern == "*" or pattern in key:
                        keys_to_remove.append(key)
                
                for key in keys_to_remove:
                    entry = self.l1_cache.pop(key)
                    if self.enable_metrics:
                        cache_items.labels(level="l1").dec()
                        cache_size.labels(level="l1").dec(entry.size_bytes)
                    cleared_count += 1
            
            # Limpa L2 (Redis)
            if self.redis_client and pattern != "*":
                # Para padrões específicos, busca chaves correspondentes
                keys = await self.redis_client.keys(f"*{pattern}*")
                if keys:
                    await self.redis_client.delete(*keys)
                    cleared_count += len(keys) // 2  # meta + data keys
            elif self.redis_client and pattern == "*":
                # Limpa tudo
                await self.redis_client.flushdb()
            
            return cleared_count
            
        except Exception as e:
            logger.error(f"Error clearing cache with pattern {pattern}: {e}")
            return 0

    async def _check_auto_refresh(self, key: str, entry: CacheEntry):
        """Verifica se deve fazer auto-refresh do valor"""
        if key not in self.refresh_callbacks:
            return
        
        if not entry.expires_at:
            return
        
        # Calcula se está próximo da expiração
        now = datetime.now()
        time_to_expire = (entry.expires_at - now).total_seconds()
        total_ttl = (entry.expires_at - entry.created_at).total_seconds()
        
        if time_to_expire / total_ttl <= (1 - self.auto_refresh_threshold):
            # Inicia refresh assíncrono se não estiver já rodando
            if key not in self.refresh_tasks or self.refresh_tasks[key].done():
                self.refresh_tasks[key] = asyncio.create_task(self._refresh_key(key))

    async def _refresh_key(self, key: str):
        """Executa refresh assíncrono de uma chave"""
        try:
            callback = self.refresh_callbacks.get(key)
            if not callback:
                return
            
            logger.debug(f"Auto-refreshing cache key: {key}")
            
            # Executa callback em thread pool para não bloquear
            loop = asyncio.get_event_loop()
            new_value = await loop.run_in_executor(self.refresh_executor, callback)
            
            if new_value is not None:
                # Atualiza cache com novo valor
                await self.set(key, new_value, refresh_callback=callback)
                logger.debug(f"Successfully refreshed cache key: {key}")
            
        except Exception as e:
            logger.error(f"Error refreshing cache key {key}: {e}")

    def _get_key_type(self, key: str) -> str:
        """Determina tipo da chave baseado no prefixo"""
        if key.startswith("stock:"):
            return "stock_data"
        elif key.startswith("analysis:"):
            return "analysis"
        elif key.startswith("methodology:"):
            return "methodology"
        elif key.startswith("user:"):
            return "user_data"
        else:
            return "unknown"

    async def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas detalhadas do cache"""
        with self.l1_lock:
            l1_size_bytes = sum(entry.size_bytes for entry in self.l1_cache.values())
            l1_item_count = len(self.l1_cache)
        
        # Estatísticas L2 (Redis)
        l2_info = {}
        if self.redis_client:
            try:
                info = await self.redis_client.info('memory')
                l2_info = {
                    'used_memory': info.get('used_memory', 0),
                    'used_memory_human': info.get('used_memory_human', '0B'),
                    'maxmemory': info.get('maxmemory', 0)
                }
            except:
                pass
        
        return {
            'l1': {
                'hits': self.l1_stats.hits,
                'misses': self.l1_stats.misses,
                'evictions': self.l1_stats.evictions,
                'size_bytes': l1_size_bytes,
                'item_count': l1_item_count,
                'hit_ratio': self.l1_stats.hits / max(self.l1_stats.hits + self.l1_stats.misses, 1),
                'max_size': self.l1_max_size,
                'max_memory': self.l1_max_memory
            },
            'l2': {
                'hits': self.l2_stats.hits,
                'misses': self.l2_stats.misses,
                'redis_info': l2_info
            },
            'refresh': {
                'active_callbacks': len(self.refresh_callbacks),
                'active_tasks': len([t for t in self.refresh_tasks.values() if not t.done()])
            }
        }

# Instância global do cache
cache = AdvancedCache()

# Funções de conveniência
async def get(key: str, default: Any = None) -> Any:
    """Função de conveniência para buscar no cache"""
    return await cache.get(key, default)

async def set(key: str, value: Any, ttl: Optional[int] = None, key_type: str = "unknown", refresh_callback: Optional[callable] = None) -> bool:
    """Função de conveniência para definir no cache"""
    return await cache.set(key, value, ttl, key_type, refresh_callback)

async def delete(key: str) -> bool:
    """Função de conveniência para deletar do cache"""
    return await cache.delete(key)

async def clear(pattern: str = "*") -> int:
    """Função de conveniência para limpar cache"""
    return await cache.clear(pattern)

