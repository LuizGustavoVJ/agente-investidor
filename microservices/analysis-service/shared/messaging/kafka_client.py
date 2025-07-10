"""
Cliente Kafka compartilhado para todos os microserviços
"""

import os
import json
import asyncio
from typing import Dict, Any, Callable, Optional, List
from datetime import datetime
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import structlog

logger = structlog.get_logger()

class KafkaClient:
    """Cliente Kafka para produção e consumo de mensagens"""
    
    def __init__(self, bootstrap_servers: str = None):
        self.bootstrap_servers = bootstrap_servers or os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
        self.producer = None
        self.consumers = {}
        
    def get_producer(self) -> KafkaProducer:
        """Obter producer Kafka (singleton)"""
        if not self.producer:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',  # Aguardar confirmação de todas as réplicas
                retries=3,
                retry_backoff_ms=1000,
                request_timeout_ms=30000,
                compression_type='gzip'
            )
        return self.producer
    
    def send_message(self, topic: str, message: Dict[str, Any], key: str = None) -> bool:
        """Enviar mensagem para um tópico"""
        try:
            producer = self.get_producer()
            
            # Adicionar metadata
            enriched_message = {
                **message,
                'timestamp': datetime.utcnow().isoformat(),
                'source_service': os.getenv('SERVICE_NAME', 'unknown')
            }
            
            future = producer.send(topic, value=enriched_message, key=key)
            record_metadata = future.get(timeout=10)
            
            logger.info(
                "Message sent successfully",
                topic=topic,
                partition=record_metadata.partition,
                offset=record_metadata.offset,
                key=key
            )
            return True
            
        except KafkaError as e:
            logger.error("Failed to send message", topic=topic, error=str(e))
            return False
        except Exception as e:
            logger.error("Unexpected error sending message", topic=topic, error=str(e))
            return False
    
    def create_consumer(self, topics: List[str], group_id: str, 
                       auto_offset_reset: str = 'latest') -> KafkaConsumer:
        """Criar consumer Kafka"""
        consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=self.bootstrap_servers,
            group_id=group_id,
            auto_offset_reset=auto_offset_reset,
            enable_auto_commit=True,
            auto_commit_interval_ms=1000,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            consumer_timeout_ms=1000
        )
        return consumer
    
    def consume_messages(self, topics: List[str], group_id: str, 
                        message_handler: Callable[[str, Dict[str, Any]], None],
                        auto_offset_reset: str = 'latest'):
        """Consumir mensagens de tópicos"""
        consumer = self.create_consumer(topics, group_id, auto_offset_reset)
        
        logger.info("Starting message consumption", topics=topics, group_id=group_id)
        
        try:
            for message in consumer:
                try:
                    topic = message.topic
                    value = message.value
                    key = message.key
                    
                    logger.debug(
                        "Message received",
                        topic=topic,
                        partition=message.partition,
                        offset=message.offset,
                        key=key
                    )
                    
                    # Processar mensagem
                    message_handler(topic, value)
                    
                except Exception as e:
                    logger.error(
                        "Error processing message",
                        topic=message.topic,
                        error=str(e),
                        message=message.value
                    )
                    
        except KeyboardInterrupt:
            logger.info("Consumer interrupted")
        except Exception as e:
            logger.error("Consumer error", error=str(e))
        finally:
            consumer.close()
            logger.info("Consumer closed")
    
    def close(self):
        """Fechar conexões"""
        if self.producer:
            self.producer.close()
        
        for consumer in self.consumers.values():
            consumer.close()

# Tópicos padrão do sistema
class Topics:
    # Eventos de análise
    ANALYSIS_REQUESTED = "analysis.requested"
    ANALYSIS_COMPLETED = "analysis.completed"
    ANALYSIS_FAILED = "analysis.failed"
    
    # Eventos de metodologias
    METHODOLOGY_ANALYSIS_REQUESTED = "methodology.analysis.requested"
    METHODOLOGY_ANALYSIS_COMPLETED = "methodology.analysis.completed"
    
    # Eventos de dados
    STOCK_DATA_UPDATED = "stock.data.updated"
    MARKET_DATA_UPDATED = "market.data.updated"
    
    # Eventos de usuário
    USER_REGISTERED = "user.registered"
    USER_LOGIN = "user.login"
    USER_ANALYSIS_REQUESTED = "user.analysis.requested"
    
    # Eventos de sistema
    CACHE_INVALIDATED = "cache.invalidated"
    SERVICE_HEALTH_CHECK = "service.health.check"
    
    # Notificações
    NOTIFICATION_SEND = "notification.send"
    EMAIL_SEND = "email.send"

# Schemas de mensagens
class MessageSchemas:
    
    @staticmethod
    def analysis_requested(user_id: str, symbol: str, methodologies: List[str] = None) -> Dict[str, Any]:
        return {
            "event_type": "analysis_requested",
            "user_id": user_id,
            "symbol": symbol,
            "methodologies": methodologies or [],
            "request_id": f"req_{datetime.utcnow().timestamp()}"
        }
    
    @staticmethod
    def analysis_completed(request_id: str, symbol: str, results: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "event_type": "analysis_completed",
            "request_id": request_id,
            "symbol": symbol,
            "results": results,
            "completed_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def stock_data_updated(symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "event_type": "stock_data_updated",
            "symbol": symbol,
            "data": data,
            "updated_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def user_registered(user_id: str, email: str) -> Dict[str, Any]:
        return {
            "event_type": "user_registered",
            "user_id": user_id,
            "email": email,
            "registered_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def cache_invalidated(service: str, keys: List[str]) -> Dict[str, Any]:
        return {
            "event_type": "cache_invalidated",
            "service": service,
            "keys": keys,
            "invalidated_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def notification_send(user_id: str, title: str, message: str, 
                         notification_type: str = "info") -> Dict[str, Any]:
        return {
            "event_type": "notification_send",
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": notification_type,
            "created_at": datetime.utcnow().isoformat()
        }

# Singleton global
kafka_client = KafkaClient()

# Funções de conveniência
def send_message(topic: str, message: Dict[str, Any], key: str = None) -> bool:
    """Função global para enviar mensagens"""
    return kafka_client.send_message(topic, message, key)

def consume_messages(topics: List[str], group_id: str, 
                    message_handler: Callable[[str, Dict[str, Any]], None],
                    auto_offset_reset: str = 'latest'):
    """Função global para consumir mensagens"""
    return kafka_client.consume_messages(topics, group_id, message_handler, auto_offset_reset)

