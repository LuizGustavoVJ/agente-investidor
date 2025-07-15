"""
Serviço de Relatórios - Agente Investidor
Responsável por gerar relatórios em múltiplos formatos (PDF, Excel, CSV)
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_client import start_http_server
import structlog
import time
import redis
import json
import httpx
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import uuid
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io
import tempfile
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
REQUEST_COUNT = Counter('report_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('report_request_duration_seconds', 'Request duration')
REPORTS_GENERATED = Counter('reports_generated_total', 'Reports generated', ['format'])

# Redis connection
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=7,  # DB específico para relatórios
    decode_responses=True
)

# FastAPI app
app = FastAPI(
    title="Agente Investidor - Report Service",
    description="Serviço de Geração de Relatórios",
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
class ReportFormat(str, Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"

class ReportType(str, Enum):
    PORTFOLIO_SUMMARY = "portfolio_summary"
    ANALYSIS_REPORT = "analysis_report"
    PERFORMANCE_REPORT = "performance_report"
    RISK_REPORT = "risk_report"
    COMPARISON_REPORT = "comparison_report"
    CUSTOM_REPORT = "custom_report"

# Models
class ReportRequest(BaseModel):
    user_id: str
    report_type: ReportType
    format: ReportFormat
    parameters: Dict[str, Any] = Field(default_factory=dict)
    include_charts: bool = True
    include_tables: bool = True
    custom_title: Optional[str] = None
    custom_description: Optional[str] = None

class Report(BaseModel):
    report_id: str
    user_id: str
    report_type: ReportType
    format: ReportFormat
    title: str
    description: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    generation_time: Optional[float] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    status: str = "pending"  # pending, generating, completed, failed
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class ReportTemplate(BaseModel):
    template_id: str
    name: str
    description: Optional[str] = None
    report_type: ReportType
    format: ReportFormat
    template_data: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

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

async def fetch_data_from_service(service_url: str, endpoint: str) -> Optional[Dict[str, Any]]:
    """Buscar dados de outros serviços"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{service_url}{endpoint}")
            if response.status_code == 200:
                return response.json()
            return None
    except Exception as e:
        logger.error("Error fetching data from service", service_url=service_url, endpoint=endpoint, error=str(e))
        return None

def generate_pdf_report(report_data: Dict[str, Any], title: str) -> bytes:
    """Gerar relatório em PDF"""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center
        )
        
        # Título
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 12))
        
        # Dados do relatório
        for section_title, section_data in report_data.items():
            # Título da seção
            story.append(Paragraph(f"<b>{section_title}</b>", styles['Heading2']))
            story.append(Spacer(1, 6))
            
            if isinstance(section_data, dict):
                # Criar tabela para dados estruturados
                table_data = []
                for key, value in section_data.items():
                    table_data.append([key, str(value)])
                
                if table_data:
                    table = Table(table_data, colWidths=[2*inch, 4*inch])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 12),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 10),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(table)
            else:
                # Texto simples
                story.append(Paragraph(str(section_data), styles['Normal']))
            
            story.append(Spacer(1, 12))
        
        # Gerar PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        logger.error("Error generating PDF report", error=str(e))
        raise

def generate_excel_report(report_data: Dict[str, Any], title: str) -> bytes:
    """Gerar relatório em Excel"""
    try:
        # Criar DataFrame
        df_data = []
        for section_title, section_data in report_data.items():
            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    df_data.append({
                        'Seção': section_title,
                        'Campo': key,
                        'Valor': str(value)
                    })
            else:
                df_data.append({
                    'Seção': section_title,
                    'Campo': 'Conteúdo',
                    'Valor': str(section_data)
                })
        
        df = pd.DataFrame(df_data)
        
        # Criar Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Relatório', index=False)
            
            # Formatação básica
            workbook = writer.book
            worksheet = writer.sheets['Relatório']
            
            # Adicionar título
            worksheet.insert_rows(1)
            worksheet['A1'] = title
            worksheet.merge_cells('A1:C1')
        
        output.seek(0)
        return output.getvalue()
        
    except Exception as e:
        logger.error("Error generating Excel report", error=str(e))
        raise

def generate_csv_report(report_data: Dict[str, Any], title: str) -> bytes:
    """Gerar relatório em CSV"""
    try:
        # Criar DataFrame
        df_data = []
        for section_title, section_data in report_data.items():
            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    df_data.append({
                        'Seção': section_title,
                        'Campo': key,
                        'Valor': str(value)
                    })
            else:
                df_data.append({
                    'Seção': section_title,
                    'Campo': 'Conteúdo',
                    'Valor': str(section_data)
                })
        
        df = pd.DataFrame(df_data)
        
        # Gerar CSV
        output = io.BytesIO()
        df.to_csv(output, index=False, encoding='utf-8')
        output.seek(0)
        return output.getvalue()
        
    except Exception as e:
        logger.error("Error generating CSV report", error=str(e))
        raise

async def generate_portfolio_summary_report(user_id: str, format: ReportFormat) -> Dict[str, Any]:
    """Gerar relatório de resumo do portfólio"""
    try:
        # Buscar dados do portfólio
        portfolio_data = await fetch_data_from_service(
            "http://dashboard-service:8006",
            f"/metrics/portfolio/{user_id}"
        )
        
        performance_data = await fetch_data_from_service(
            "http://dashboard-service:8006",
            f"/performance/{user_id}?period=1y"
        )
        
        # Estruturar dados para o relatório
        report_data = {
            "Resumo do Portfólio": {
                "Valor Total": f"R$ {portfolio_data.get('total_value', 0):,.2f}",
                "Variação Total": f"R$ {portfolio_data.get('total_change', 0):,.2f}",
                "Variação Percentual": f"{portfolio_data.get('total_change_percent', 0):.2f}%",
                "Variação Diária": f"R$ {portfolio_data.get('daily_change', 0):,.2f}",
                "Moeda": portfolio_data.get('currency', 'BRL')
            },
            "Performance": {
                "Período": "1 ano",
                "Valor Inicial": f"R$ {performance_data.get('values', [0])[0]:,.2f}",
                "Valor Final": f"R$ {performance_data.get('values', [0])[-1]:,.2f}",
                "Retorno Total": f"{((performance_data.get('values', [0])[-1] / performance_data.get('values', [0])[0] - 1) * 100):.2f}%"
            },
            "Informações Gerais": {
                "Data de Geração": datetime.utcnow().strftime("%d/%m/%Y %H:%M"),
                "Usuário": user_id,
                "Tipo de Relatório": "Resumo do Portfólio"
            }
        }
        
        return report_data
        
    except Exception as e:
        logger.error("Error generating portfolio summary report", user_id=user_id, error=str(e))
        raise

async def generate_analysis_report(user_id: str, symbol: str, format: ReportFormat) -> Dict[str, Any]:
    """Gerar relatório de análise"""
    try:
        # Buscar dados de análise
        analysis_data = await fetch_data_from_service(
            "http://analysis-service:8003",
            f"/analysis/{symbol}"
        )
        
        methodology_data = await fetch_data_from_service(
            "http://methodology-service:8004",
            f"/methodologies"
        )
        
        # Estruturar dados para o relatório
        report_data = {
            "Análise da Ação": {
                "Símbolo": symbol,
                "Nome": analysis_data.get('company_name', 'N/A'),
                "Setor": analysis_data.get('sector', 'N/A'),
                "Score Geral": f"{analysis_data.get('overall_score', 0):.1f}/100"
            },
            "Indicadores Financeiros": {
                "P/L": f"{analysis_data.get('indicators', {}).get('pe_ratio', 0):.2f}",
                "P/VP": f"{analysis_data.get('indicators', {}).get('pb_ratio', 0):.2f}",
                "ROE": f"{analysis_data.get('indicators', {}).get('roe', 0):.2f}%",
                "Margem Líquida": f"{analysis_data.get('indicators', {}).get('net_margin', 0):.2f}%"
            },
            "Recomendações": {
                "Recomendação": analysis_data.get('recommendation', 'N/A'),
                "Justificativa": analysis_data.get('justification', 'N/A'),
                "Risco": analysis_data.get('risk_level', 'N/A')
            },
            "Metodologias Aplicadas": {
                "Total de Metodologias": len(methodology_data.get('methodologies', [])),
                "Metodologias Utilizadas": ", ".join([m.get('name', '') for m in methodology_data.get('methodologies', [])])
            },
            "Informações Gerais": {
                "Data de Geração": datetime.utcnow().strftime("%d/%m/%Y %H:%M"),
                "Usuário": user_id,
                "Tipo de Relatório": "Análise de Ação"
            }
        }
        
        return report_data
        
    except Exception as e:
        logger.error("Error generating analysis report", user_id=user_id, symbol=symbol, error=str(e))
        raise

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
            "service": "report-service",
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

# Report generation endpoints
@app.post("/reports", response_model=Report)
async def create_report(request: ReportRequest):
    """Criar novo relatório"""
    try:
        report = Report(
            report_id=str(uuid.uuid4()),
            user_id=request.user_id,
            report_type=request.report_type,
            format=request.format,
            title=request.custom_title or f"Relatório {request.report_type.value}",
            description=request.custom_description,
            parameters=request.parameters,
            created_at=datetime.utcnow()
        )
        
        # Salvar no cache
        cache_key = get_cache_key("report", report_id=report.report_id)
        cache_data(cache_key, report.dict(), 86400)
        
        # Processar relatório em background
        asyncio.create_task(generate_report_async(report))
        
        return report
        
    except Exception as e:
        logger.error("Error creating report", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

async def generate_report_async(report: Report):
    """Gerar relatório de forma assíncrona"""
    try:
        start_time = time.time()
        report.status = "generating"
        
        # Atualizar status no cache
        cache_key = get_cache_key("report", report_id=report.report_id)
        cache_data(cache_key, report.dict(), 86400)
        
        # Gerar dados do relatório baseado no tipo
        if report.report_type == ReportType.PORTFOLIO_SUMMARY:
            report_data = await generate_portfolio_summary_report(report.user_id, report.format)
        elif report.report_type == ReportType.ANALYSIS_REPORT:
            symbol = report.parameters.get('symbol', 'PETR4')
            report_data = await generate_analysis_report(report.user_id, symbol, report.format)
        else:
            # Relatório genérico
            report_data = {
                "Informações Gerais": {
                    "Data de Geração": datetime.utcnow().strftime("%d/%m/%Y %H:%M"),
                    "Usuário": report.user_id,
                    "Tipo de Relatório": report.report_type.value
                }
            }
        
        # Gerar arquivo baseado no formato
        file_content = None
        file_extension = ""
        
        if report.format == ReportFormat.PDF:
            file_content = generate_pdf_report(report_data, report.title)
            file_extension = "pdf"
        elif report.format == ReportFormat.EXCEL:
            file_content = generate_excel_report(report_data, report.title)
            file_extension = "xlsx"
        elif report.format == ReportFormat.CSV:
            file_content = generate_csv_report(report_data, report.title)
            file_extension = "csv"
        elif report.format == ReportFormat.JSON:
            file_content = json.dumps(report_data, indent=2, default=str).encode('utf-8')
            file_extension = "json"
        
        # Salvar arquivo
        filename = f"{report.report_id}.{file_extension}"
        file_path = f"/tmp/reports/{filename}"
        
        # Criar diretório se não existir
        os.makedirs("/tmp/reports", exist_ok=True)
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Atualizar relatório
        report.status = "completed"
        report.file_path = file_path
        report.file_size = len(file_content)
        report.generation_time = time.time() - start_time
        report.completed_at = datetime.utcnow()
        
        # Atualizar cache
        cache_data(cache_key, report.dict(), 86400)
        
        REPORTS_GENERATED.labels(format=report.format.value).inc()
        
        logger.info("Report generated successfully", 
                   report_id=report.report_id, 
                   format=report.format.value,
                   generation_time=report.generation_time)
        
    except Exception as e:
        logger.error("Error generating report", report_id=report.report_id, error=str(e))
        
        # Atualizar status de erro
        report.status = "failed"
        report.error_message = str(e)
        report.completed_at = datetime.utcnow()
        
        cache_key = get_cache_key("report", report_id=report.report_id)
        cache_data(cache_key, report.dict(), 86400)

@app.get("/reports/{report_id}", response_model=Report)
async def get_report(report_id: str):
    """Obter relatório por ID"""
    try:
        cache_key = get_cache_key("report", report_id=report_id)
        report_data = get_cached_data(cache_key)
        
        if not report_data:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return Report(**report_data)
        
    except Exception as e:
        logger.error("Error getting report", report_id=report_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/reports/{report_id}/download")
async def download_report(report_id: str):
    """Baixar arquivo do relatório"""
    try:
        cache_key = get_cache_key("report", report_id=report_id)
        report_data = get_cached_data(cache_key)
        
        if not report_data:
            raise HTTPException(status_code=404, detail="Report not found")
        
        report = Report(**report_data)
        
        if report.status != "completed":
            raise HTTPException(status_code=400, detail="Report not ready for download")
        
        if not report.file_path or not os.path.exists(report.file_path):
            raise HTTPException(status_code=404, detail="Report file not found")
        
        # Determinar content type
        content_type_map = {
            "pdf": "application/pdf",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "csv": "text/csv",
            "json": "application/json"
        }
        
        file_extension = report.file_path.split('.')[-1]
        content_type = content_type_map.get(file_extension, "application/octet-stream")
        
        return FileResponse(
            path=report.file_path,
            media_type=content_type,
            filename=f"{report.title}.{file_extension}"
        )
        
    except Exception as e:
        logger.error("Error downloading report", report_id=report_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/reports/user/{user_id}", response_model=List[Report])
async def get_user_reports(user_id: str, limit: int = 50):
    """Obter relatórios do usuário"""
    try:
        # Buscar relatórios do cache
        pattern = f"report:*"
        keys = redis_client.keys(pattern)
        
        reports = []
        for key in keys[:limit]:
            report_data = get_cached_data(key)
            if report_data and report_data.get("user_id") == user_id:
                reports.append(Report(**report_data))
        
        # Ordenar por data de criação (mais recente primeiro)
        reports.sort(key=lambda x: x.created_at, reverse=True)
        
        return reports
        
    except Exception as e:
        logger.error("Error getting user reports", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# Template endpoints
@app.get("/templates", response_model=List[ReportTemplate])
async def get_report_templates():
    """Obter templates de relatório"""
    try:
        cache_key = get_cache_key("report_templates")
        cached_templates = get_cached_data(cache_key)
        
        if cached_templates:
            return [ReportTemplate(**template) for template in cached_templates]
        
        # Templates padrão
        default_templates = [
            {
                "template_id": str(uuid.uuid4()),
                "name": "Resumo do Portfólio",
                "description": "Relatório resumido do portfólio de investimentos",
                "report_type": ReportType.PORTFOLIO_SUMMARY,
                "format": ReportFormat.PDF,
                "template_data": {
                    "sections": ["Resumo do Portfólio", "Performance", "Informações Gerais"]
                },
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "template_id": str(uuid.uuid4()),
                "name": "Análise de Ação",
                "description": "Relatório detalhado de análise de ação",
                "report_type": ReportType.ANALYSIS_REPORT,
                "format": ReportFormat.EXCEL,
                "template_data": {
                    "sections": ["Análise da Ação", "Indicadores Financeiros", "Recomendações"]
                },
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        cache_data(cache_key, default_templates, 3600)
        
        return [ReportTemplate(**template) for template in default_templates]
        
    except Exception as e:
        logger.error("Error getting report templates", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008) 