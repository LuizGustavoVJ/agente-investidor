"""
Serviço de Notificações - Agente Investidor
Responsável por enviar notificações através de múltiplos canais
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_client import start_http_server
import structlog
import time
import redis
import json
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr, Field
import uuid
import asyncio
from enum import Enum

# Configuração de logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Métricas Prometheus
REQUEST_COUNT = Counter('notification_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('notification_request_duration_seconds', 'Request duration')
NOTIFICATIONS_SENT = Counter('notifications_sent_total', 'Notifications sent', ['channel', 'status'])

# Redis connection
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=6,  # DB específico para notificações
    decode_responses=True
)

# FastAPI app
app = FastAPI(
    title="Agente Investidor - Notification Service",
    description="Serviço de Notificações Multi-canal",
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

# Enums
class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    SLACK = "slack"

class NotificationPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"
    READ = "read"

# Models
class NotificationTemplate(BaseModel):
    template_id: str
    name: str
    description: Optional[str] = None
    subject: str
    body: str
    channels: List[NotificationChannel]
    variables: List[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Notification(BaseModel):
    notification_id: str
    user_id: str
    template_id: Optional[str] = None
    channel: NotificationChannel
    subject: str
    message: str
    recipient: str  # email, phone, user_id
    priority: NotificationPriority = NotificationPriority.NORMAL
    status: NotificationStatus = NotificationStatus.PENDING
    metadata: Dict[str, Any] = Field(default_factory=dict)
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class NotificationRequest(BaseModel):
    user_id: str
    template_id: Optional[str] = None
    channel: NotificationChannel
    subject: str
    message: str
    recipient: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    metadata: Dict[str, Any] = Field(default_factory=dict)
    scheduled_at: Optional[datetime] = None

class NotificationCampaign(BaseModel):
    campaign_id: str
    name: str
    description: Optional[str] = None
    template_id: str
    user_ids: List[str]
    channels: List[NotificationChannel]
    priority: NotificationPriority = NotificationPriority.NORMAL
    scheduled_at: Optional[datetime] = None
    status: str = "draft"  # draft, scheduled, running, completed, cancelled
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Email configuration
EMAIL_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "username": os.getenv("EMAIL_USERNAME", ""),
    "password": os.getenv("EMAIL_PASSWORD", ""),
    "from_email": os.getenv("FROM_EMAIL", "noreply@agenteinvestidor.com"),
    "from_name": os.getenv("FROM_NAME", "Agente Investidor")
}

# Utility functions
def get_cache_key(prefix: str, **kwargs) -> str:
    """Gerar chave de cache"""
    key_parts = [prefix]
    for k, v in kwargs.items():
        key_parts.append(f"{k}:{v}")
    return ":".join(key_parts)

def cache_data(key: str, data: Any, ttl: int = 1800):
    """Salvar dados no cache"""
    try:
        redis_client.setex(key, ttl, json.dumps(data, default=str))
    except Exception as e:
        logger.error("Cache save failed", key=key, error=str(e))

def get_cached_data(key: str) -> Optional[Any]:
    """Recuperar dados do cache"""
    try:
        cached = redis_client.get(key)
        if cached:
            return json.loads(cached)
        return None
    except Exception as e:
        logger.error("Cache read failed", key=key, error=str(e))
        return None

def send_email_notification(notification: Notification) -> bool:
    """Enviar notificação por email"""
    try:
        # Configurar mensagem
        msg = MIMEMultipart()
        msg['From'] = f"{EMAIL_CONFIG['from_name']} <{EMAIL_CONFIG['from_email']}>"
        msg['To'] = notification.recipient
        msg['Subject'] = notification.subject
        
        # Adicionar corpo da mensagem
        msg.attach(MIMEText(notification.message, 'html'))
        
        # Enviar email
        context = ssl.create_default_context()
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls(context=context)
            if EMAIL_CONFIG['username'] and EMAIL_CONFIG['password']:
                server.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
            server.send_message(msg)
        
        logger.info("Email notification sent", notification_id=notification.notification_id, recipient=notification.recipient)
        NOTIFICATIONS_SENT.labels(channel="email", status="sent").inc()
        return True
        
    except Exception as e:
        logger.error("Error sending email notification", notification_id=notification.notification_id, error=str(e))
        NOTIFICATIONS_SENT.labels(channel="email", status="failed").inc()
        return False

def send_sms_notification(notification: Notification) -> bool:
    """Enviar notificação por SMS (simulado)"""
    try:
        # Simular envio de SMS
        logger.info("SMS notification sent", notification_id=notification.notification_id, recipient=notification.recipient)
        NOTIFICATIONS_SENT.labels(channel="sms", status="sent").inc()
        return True
        
    except Exception as e:
        logger.error("Error sending SMS notification", notification_id=notification.notification_id, error=str(e))
        NOTIFICATIONS_SENT.labels(channel="sms", status="failed").inc()
        return False

def send_push_notification(notification: Notification) -> bool:
    """Enviar notificação push (simulado)"""
    try:
        # Simular envio de push notification
        logger.info("Push notification sent", notification_id=notification.notification_id, recipient=notification.recipient)
        NOTIFICATIONS_SENT.labels(channel="push", status="sent").inc()
        return True
        
    except Exception as e:
        logger.error("Error sending push notification", notification_id=notification.notification_id, error=str(e))
        NOTIFICATIONS_SENT.labels(channel="push", status="failed").inc()
        return False

def send_webhook_notification(notification: Notification) -> bool:
    """Enviar notificação via webhook"""
    try:
        # Simular envio de webhook
        webhook_url = notification.metadata.get("webhook_url")
        if webhook_url:
            logger.info("Webhook notification sent", notification_id=notification.notification_id, webhook_url=webhook_url)
            NOTIFICATIONS_SENT.labels(channel="webhook", status="sent").inc()
            return True
        else:
            logger.error("Webhook URL not provided", notification_id=notification.notification_id)
            NOTIFICATIONS_SENT.labels(channel="webhook", status="failed").inc()
            return False
            
    except Exception as e:
        logger.error("Error sending webhook notification", notification_id=notification.notification_id, error=str(e))
        NOTIFICATIONS_SENT.labels(channel="webhook", status="failed").inc()
        return False

def send_slack_notification(notification: Notification) -> bool:
    """Enviar notificação para Slack"""
    try:
        # Simular envio para Slack
        slack_channel = notification.metadata.get("slack_channel", "#general")
        logger.info("Slack notification sent", notification_id=notification.notification_id, channel=slack_channel)
        NOTIFICATIONS_SENT.labels(channel="slack", status="sent").inc()
        return True
        
    except Exception as e:
        logger.error("Error sending Slack notification", notification_id=notification.notification_id, error=str(e))
        NOTIFICATIONS_SENT.labels(channel="slack", status="failed").inc()
        return False

async def send_notification(notification: Notification) -> bool:
    """Enviar notificação baseado no canal"""
    try:
        success = False
        
        if notification.channel == NotificationChannel.EMAIL:
            success = send_email_notification(notification)
        elif notification.channel == NotificationChannel.SMS:
            success = send_sms_notification(notification)
        elif notification.channel == NotificationChannel.PUSH:
            success = send_push_notification(notification)
        elif notification.channel == NotificationChannel.WEBHOOK:
            success = send_webhook_notification(notification)
        elif notification.channel == NotificationChannel.SLACK:
            success = send_slack_notification(notification)
        
        if success:
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.utcnow()
        else:
            notification.status = NotificationStatus.FAILED
            notification.retry_count += 1
        
        notification.updated_at = datetime.utcnow()
        
        # Atualizar no cache
        cache_key = get_cache_key("notification", notification_id=notification.notification_id)
        cache_data(cache_key, notification.dict(), 86400)  # 24 horas
        
        return success
        
    except Exception as e:
        logger.error("Error sending notification", notification_id=notification.notification_id, error=str(e))
        return False

# Middleware para métricas
@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.observe(duration)
    
    return response

# Health check
@app.get("/health")
async def health_check():
    try:
        # Verificar Redis
        redis_client.ping()
        
        return {
            "status": "healthy",
            "service": "notification-service",
            "timestamp": datetime.utcnow().isoformat(),
            "dependencies": {
                "redis": "healthy"
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Métricas endpoint
@app.get("/metrics")
async def metrics():
    return generate_latest()

# Template endpoints
@app.get("/templates", response_model=List[NotificationTemplate])
async def get_notification_templates():
    """Obter todos os templates de notificação"""
    try:
        cache_key = get_cache_key("templates")
        cached_templates = get_cached_data(cache_key)
        
        if cached_templates:
            return [NotificationTemplate(**template) for template in cached_templates]
        
        # Templates padrão
        default_templates = [
            {
                "template_id": str(uuid.uuid4()),
                "name": "Welcome Email",
                "description": "Email de boas-vindas para novos usuários",
                "subject": "Bem-vindo ao Agente Investidor!",
                "body": """
                <h2>Olá {{user_name}}!</h2>
                <p>Bem-vindo ao Agente Investidor. Sua conta foi criada com sucesso.</p>
                <p>Comece a explorar nossas funcionalidades:</p>
                <ul>
                    <li>Análises de ações</li>
                    <li>Metodologias de investimento</li>
                    <li>Dashboards personalizados</li>
                </ul>
                """,
                "channels": [NotificationChannel.EMAIL],
                "variables": ["user_name"],
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "template_id": str(uuid.uuid4()),
                "name": "Analysis Complete",
                "description": "Notificação quando análise é concluída",
                "subject": "Análise concluída: {{symbol}}",
                "body": """
                <h2>Análise Concluída</h2>
                <p>A análise de {{symbol}} foi concluída.</p>
                <p><strong>Recomendação:</strong> {{recommendation}}</p>
                <p><strong>Score:</strong> {{score}}/100</p>
                """,
                "channels": [NotificationChannel.EMAIL, NotificationChannel.PUSH],
                "variables": ["symbol", "recommendation", "score"],
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "template_id": str(uuid.uuid4()),
                "name": "Market Alert",
                "description": "Alertas de mercado importantes",
                "subject": "Alerta de Mercado: {{alert_type}}",
                "body": """
                <h2>Alerta de Mercado</h2>
                <p><strong>Tipo:</strong> {{alert_type}}</p>
                <p><strong>Descrição:</strong> {{description}}</p>
                <p><strong>Impacto:</strong> {{impact}}</p>
                """,
                "channels": [NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.PUSH],
                "variables": ["alert_type", "description", "impact"],
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        cache_data(cache_key, default_templates, 3600)  # 1 hora
        
        return [NotificationTemplate(**template) for template in default_templates]
        
    except Exception as e:
        logger.error("Error getting notification templates", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/templates", response_model=NotificationTemplate)
async def create_notification_template(template: NotificationTemplate):
    """Criar novo template de notificação"""
    try:
        template.template_id = str(uuid.uuid4())
        template.created_at = datetime.utcnow()
        template.updated_at = datetime.utcnow()
        
        # Adicionar ao cache
        cache_key = get_cache_key("templates")
        cached_templates = get_cached_data(cache_key) or []
        cached_templates.append(template.dict())
        cache_data(cache_key, cached_templates, 3600)
        
        return template
        
    except Exception as e:
        logger.error("Error creating notification template", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# Notification endpoints
@app.post("/notifications", response_model=Notification)
async def create_notification(request: NotificationRequest):
    """Criar nova notificação"""
    try:
        notification = Notification(
            notification_id=str(uuid.uuid4()),
            user_id=request.user_id,
            template_id=request.template_id,
            channel=request.channel,
            subject=request.subject,
            message=request.message,
            recipient=request.recipient,
            priority=request.priority,
            metadata=request.metadata,
            scheduled_at=request.scheduled_at,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Salvar no cache
        cache_key = get_cache_key("notification", notification_id=notification.notification_id)
        cache_data(cache_key, notification.dict(), 86400)
        
        # Enviar imediatamente se não estiver agendada
        if not notification.scheduled_at:
            await send_notification(notification)
        
        return notification
        
    except Exception as e:
        logger.error("Error creating notification", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/notifications/{user_id}", response_model=List[Notification])
async def get_user_notifications(user_id: str, limit: int = 50):
    """Obter notificações do usuário"""
    try:
        # Buscar notificações do cache
        pattern = f"notification:*"
        keys = redis_client.keys(pattern)
        
        notifications = []
        for key in keys[:limit]:
            notification_data = get_cached_data(key)
            if notification_data and notification_data.get("user_id") == user_id:
                notifications.append(Notification(**notification_data))
        
        # Ordenar por data de criação (mais recente primeiro)
        notifications.sort(key=lambda x: x.created_at, reverse=True)
        
        return notifications
        
    except Exception as e:
        logger.error("Error getting user notifications", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/notifications/{notification_id}/status")
async def update_notification_status(notification_id: str, status: NotificationStatus):
    """Atualizar status da notificação"""
    try:
        cache_key = get_cache_key("notification", notification_id=notification_id)
        notification_data = get_cached_data(cache_key)
        
        if not notification_data:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        notification = Notification(**notification_data)
        notification.status = status
        notification.updated_at = datetime.utcnow()
        
        if status == NotificationStatus.READ:
            notification.read_at = datetime.utcnow()
        elif status == NotificationStatus.DELIVERED:
            notification.delivered_at = datetime.utcnow()
        
        cache_data(cache_key, notification.dict(), 86400)
        
        return {"status": "success", "message": "Notification status updated"}
        
    except Exception as e:
        logger.error("Error updating notification status", notification_id=notification_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# Campaign endpoints
@app.post("/campaigns", response_model=NotificationCampaign)
async def create_notification_campaign(campaign: NotificationCampaign):
    """Criar nova campanha de notificação"""
    try:
        campaign.campaign_id = str(uuid.uuid4())
        campaign.created_at = datetime.utcnow()
        campaign.updated_at = datetime.utcnow()
        
        # Salvar no cache
        cache_key = get_cache_key("campaign", campaign_id=campaign.campaign_id)
        cache_data(cache_key, campaign.dict(), 86400)
        
        return campaign
        
    except Exception as e:
        logger.error("Error creating notification campaign", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/campaigns/{campaign_id}/send")
async def send_campaign(campaign_id: str):
    """Enviar campanha de notificação"""
    try:
        cache_key = get_cache_key("campaign", campaign_id=campaign_id)
        campaign_data = get_cached_data(cache_key)
        
        if not campaign_data:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        campaign = NotificationCampaign(**campaign_data)
        
        # Buscar template
        templates_cache_key = get_cache_key("templates")
        templates_data = get_cached_data(templates_cache_key) or []
        
        template = None
        for t in templates_data:
            if t["template_id"] == campaign.template_id:
                template = NotificationTemplate(**t)
                break
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Enviar notificações para todos os usuários
        sent_count = 0
        failed_count = 0
        
        for user_id in campaign.user_ids:
            for channel in campaign.channels:
                notification = Notification(
                    notification_id=str(uuid.uuid4()),
                    user_id=user_id,
                    template_id=campaign.template_id,
                    channel=channel,
                    subject=template.subject,
                    message=template.body,
                    recipient=user_id,  # Em produção, buscar email/phone do usuário
                    priority=campaign.priority,
                    metadata={"campaign_id": campaign_id},
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                success = await send_notification(notification)
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
        
        # Atualizar status da campanha
        campaign.status = "completed"
        campaign.updated_at = datetime.utcnow()
        cache_data(cache_key, campaign.dict(), 86400)
        
        return {
            "status": "success",
            "message": "Campaign sent",
            "sent_count": sent_count,
            "failed_count": failed_count
        }
        
    except Exception as e:
        logger.error("Error sending campaign", campaign_id=campaign_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# Scheduled notifications
@app.get("/scheduled")
async def get_scheduled_notifications():
    """Obter notificações agendadas"""
    try:
        # Buscar notificações agendadas do cache
        pattern = f"notification:*"
        keys = redis_client.keys(pattern)
        
        scheduled_notifications = []
        now = datetime.utcnow()
        
        for key in keys:
            notification_data = get_cached_data(key)
            if notification_data:
                notification = Notification(**notification_data)
                if (notification.scheduled_at and 
                    notification.scheduled_at <= now and 
                    notification.status == NotificationStatus.PENDING):
                    scheduled_notifications.append(notification)
        
        return scheduled_notifications
        
    except Exception as e:
        logger.error("Error getting scheduled notifications", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# Background task para processar notificações agendadas
async def process_scheduled_notifications():
    """Processar notificações agendadas"""
    while True:
        try:
            scheduled_notifications = await get_scheduled_notifications()
            
            for notification in scheduled_notifications:
                await send_notification(notification)
            
            # Aguardar 1 minuto antes da próxima verificação
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error("Error processing scheduled notifications", error=str(e))
            await asyncio.sleep(60)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Iniciar tarefas em background"""
    asyncio.create_task(process_scheduled_notifications())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8007) 