"""
Testes unitários para os serviços da Fase 3
Autor: Luiz Gustavo Finotello
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from fastapi.testclient import TestClient

# Importar os serviços da Fase 3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'services'))

# Mock Redis para todos os testes
@pytest.fixture(autouse=True)
def mock_redis():
    with patch('redis.Redis') as mock_redis:
        mock_redis.return_value.ping.return_value = True
        mock_redis.return_value.get.return_value = None
        mock_redis.return_value.setex.return_value = True
        yield mock_redis

class TestUserService:
    """Testes para o User Service"""
    
    def test_user_profile_creation(self, mock_redis):
        """Testa criação de perfil de usuário"""
        from services.user_service.main import UserProfile
        
        profile = UserProfile(
            user_id="test-user",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        
        assert profile.user_id == "test-user"
        assert profile.email == "test@example.com"
        assert profile.first_name == "Test"
        assert profile.last_name == "User"
    
    def test_user_preferences_creation(self, mock_redis):
        """Testa criação de preferências de usuário"""
        from services.user_service.main import UserPreferences
        
        preferences = UserPreferences(
            user_id="test-user",
            theme="dark",
            notifications_enabled=True,
            risk_tolerance="aggressive"
        )
        
        assert preferences.user_id == "test-user"
        assert preferences.theme == "dark"
        assert preferences.notifications_enabled == True
        assert preferences.risk_tolerance == "aggressive"
    
    def test_user_settings_creation(self, mock_redis):
        """Testa criação de configurações de usuário"""
        from services.user_service.main import UserSettings
        
        settings = UserSettings(
            user_id="test-user",
            privacy_level="private",
            two_factor_auth=True,
            session_timeout=7200
        )
        
        assert settings.user_id == "test-user"
        assert settings.privacy_level == "private"
        assert settings.two_factor_auth == True
        assert settings.session_timeout == 7200

class TestDashboardService:
    """Testes para o Dashboard Service"""
    
    def test_dashboard_creation(self, mock_redis):
        """Testa criação de dashboard"""
        from services.dashboard_service.main import Dashboard
        
        dashboard = Dashboard(
            dashboard_id="test-dashboard",
            user_id="test-user",
            title="Test Dashboard",
            description="Test dashboard description"
        )
        
        assert dashboard.dashboard_id == "test-dashboard"
        assert dashboard.user_id == "test-user"
        assert dashboard.title == "Test Dashboard"
        assert dashboard.description == "Test dashboard description"
    
    def test_widget_creation(self, mock_redis):
        """Testa criação de widget"""
        from services.dashboard_service.main import Widget
        
        widget = Widget(
            widget_id="test-widget",
            dashboard_id="test-dashboard",
            widget_type="chart",
            title="Test Chart",
            position={"x": 0, "y": 0, "width": 6, "height": 4}
        )
        
        assert widget.widget_id == "test-widget"
        assert widget.dashboard_id == "test-dashboard"
        assert widget.widget_type == "chart"
        assert widget.title == "Test Chart"
        assert widget.position == {"x": 0, "y": 0, "width": 6, "height": 4}
    
    def test_portfolio_metrics_creation(self, mock_redis):
        """Testa criação de métricas de portfólio"""
        from services.dashboard_service.main import PortfolioMetric
        
        metrics = PortfolioMetric(
            total_value=100000.0,
            total_change=5000.0,
            total_change_percent=5.0,
            daily_change=1000.0,
            daily_change_percent=1.0,
            currency="BRL"
        )
        
        assert metrics.total_value == 100000.0
        assert metrics.total_change == 5000.0
        assert metrics.total_change_percent == 5.0
        assert metrics.daily_change == 1000.0
        assert metrics.daily_change_percent == 1.0
        assert metrics.currency == "BRL"

class TestNotificationService:
    """Testes para o Notification Service"""
    
    def test_notification_template_creation(self, mock_redis):
        """Testa criação de template de notificação"""
        from services.notification_service.main import NotificationTemplate, NotificationChannel
        
        template = NotificationTemplate(
            template_id="test-template",
            name="Test Template",
            description="Test template description",
            subject="Test Subject",
            body="Test body content",
            channels=[NotificationChannel.EMAIL, NotificationChannel.PUSH]
        )
        
        assert template.template_id == "test-template"
        assert template.name == "Test Template"
        assert template.subject == "Test Subject"
        assert template.body == "Test body content"
        assert NotificationChannel.EMAIL in template.channels
        assert NotificationChannel.PUSH in template.channels
    
    def test_notification_creation(self, mock_redis):
        """Testa criação de notificação"""
        from services.notification_service.main import Notification, NotificationChannel, NotificationPriority
        
        notification = Notification(
            notification_id="test-notification",
            user_id="test-user",
            channel=NotificationChannel.EMAIL,
            subject="Test Subject",
            message="Test message",
            recipient="test@example.com",
            priority=NotificationPriority.HIGH
        )
        
        assert notification.notification_id == "test-notification"
        assert notification.user_id == "test-user"
        assert notification.channel == NotificationChannel.EMAIL
        assert notification.subject == "Test Subject"
        assert notification.message == "Test message"
        assert notification.recipient == "test@example.com"
        assert notification.priority == NotificationPriority.HIGH
    
    def test_notification_campaign_creation(self, mock_redis):
        """Testa criação de campanha de notificação"""
        from services.notification_service.main import NotificationCampaign, NotificationChannel, NotificationPriority
        
        campaign = NotificationCampaign(
            campaign_id="test-campaign",
            name="Test Campaign",
            description="Test campaign description",
            template_id="test-template",
            user_ids=["user1", "user2", "user3"],
            channels=[NotificationChannel.EMAIL],
            priority=NotificationPriority.NORMAL
        )
        
        assert campaign.campaign_id == "test-campaign"
        assert campaign.name == "Test Campaign"
        assert campaign.template_id == "test-template"
        assert len(campaign.user_ids) == 3
        assert NotificationChannel.EMAIL in campaign.channels
        assert campaign.priority == NotificationPriority.NORMAL

class TestReportService:
    """Testes para o Report Service"""
    
    def test_report_request_creation(self, mock_redis):
        """Testa criação de requisição de relatório"""
        from services.report_service.main import ReportRequest, ReportType, ReportFormat
        
        request = ReportRequest(
            user_id="test-user",
            report_type=ReportType.PORTFOLIO_SUMMARY,
            format=ReportFormat.PDF,
            parameters={"period": "1y"},
            include_charts=True,
            include_tables=True
        )
        
        assert request.user_id == "test-user"
        assert request.report_type == ReportType.PORTFOLIO_SUMMARY
        assert request.format == ReportFormat.PDF
        assert request.parameters == {"period": "1y"}
        assert request.include_charts == True
        assert request.include_tables == True
    
    def test_report_creation(self, mock_redis):
        """Testa criação de relatório"""
        from services.report_service.main import Report, ReportType, ReportFormat
        
        report = Report(
            report_id="test-report",
            user_id="test-user",
            report_type=ReportType.PORTFOLIO_SUMMARY,
            format=ReportFormat.PDF,
            title="Test Report",
            description="Test report description",
            status="completed"
        )
        
        assert report.report_id == "test-report"
        assert report.user_id == "test-user"
        assert report.report_type == ReportType.PORTFOLIO_SUMMARY
        assert report.format == ReportFormat.PDF
        assert report.title == "Test Report"
        assert report.description == "Test report description"
        assert report.status == "completed"
    
    def test_report_template_creation(self, mock_redis):
        """Testa criação de template de relatório"""
        from services.report_service.main import ReportTemplate, ReportType, ReportFormat
        
        template = ReportTemplate(
            template_id="test-template",
            name="Test Template",
            description="Test template description",
            report_type=ReportType.PORTFOLIO_SUMMARY,
            format=ReportFormat.PDF,
            template_data={"sections": ["Summary", "Performance"]}
        )
        
        assert template.template_id == "test-template"
        assert template.name == "Test Template"
        assert template.report_type == ReportType.PORTFOLIO_SUMMARY
        assert template.format == ReportFormat.PDF
        assert template.template_data == {"sections": ["Summary", "Performance"]}

class TestIntegrationFase3:
    """Testes de integração para a Fase 3"""
    
    @patch('httpx.AsyncClient.get')
    def test_user_dashboard_integration(self, mock_get):
        """Testa integração entre User Service e Dashboard Service"""
        # Mock response do dashboard service
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "dashboard_id": "test-dashboard",
            "user_id": "test-user",
            "title": "Test Dashboard"
        }
        
        # Simular chamada entre serviços
        from services.dashboard_service.main import fetch_data_from_service
        
        result = fetch_data_from_service(
            "http://dashboard-service:8006",
            "/dashboards/test-user"
        )
        
        assert result is not None
        assert result["dashboard_id"] == "test-dashboard"
        assert result["user_id"] == "test-user"
    
    @patch('httpx.AsyncClient.get')
    def test_notification_report_integration(self, mock_get):
        """Testa integração entre Notification Service e Report Service"""
        # Mock response do report service
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "report_id": "test-report",
            "status": "completed",
            "file_path": "/tmp/reports/test-report.pdf"
        }
        
        # Simular chamada entre serviços
        from services.report_service.main import fetch_data_from_service
        
        result = fetch_data_from_service(
            "http://report-service:8008",
            "/reports/test-report"
        )
        
        assert result is not None
        assert result["report_id"] == "test-report"
        assert result["status"] == "completed"

class TestPerformanceFase3:
    """Testes de performance para a Fase 3"""
    
    def test_user_service_performance(self, mock_redis):
        """Testa performance do User Service"""
        import time
        
        from services.user_service.main import get_cache_key, cache_data, get_cached_data
        
        start_time = time.time()
        
        # Simular operações de cache
        for i in range(100):
            key = get_cache_key("test", user_id=f"user_{i}")
            cache_data(key, {"data": f"value_{i}"})
            get_cached_data(key)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Performance deve ser menor que 1 segundo para 100 operações
        assert execution_time < 1.0
    
    def test_dashboard_service_performance(self, mock_redis):
        """Testa performance do Dashboard Service"""
        import time
        
        from services.dashboard_service.main import get_cache_key, cache_data, get_cached_data
        
        start_time = time.time()
        
        # Simular operações de cache
        for i in range(50):
            key = get_cache_key("chart", user_id=f"user_{i}", type="performance")
            cache_data(key, {"labels": ["Jan", "Feb"], "data": [100, 110]})
            get_cached_data(key)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Performance deve ser menor que 0.5 segundos para 50 operações
        assert execution_time < 0.5

class TestSecurityFase3:
    """Testes de segurança para a Fase 3"""
    
    def test_user_data_validation(self, mock_redis):
        """Testa validação de dados do usuário"""
        from services.user_service.main import UserProfile
        from pydantic import ValidationError
        
        # Teste com email inválido
        with pytest.raises(ValidationError):
            UserProfile(
                user_id="test-user",
                email="invalid-email",
                first_name="Test",
                last_name="User"
            )
        
        # Teste com dados válidos
        try:
            profile = UserProfile(
                user_id="test-user",
                email="valid@example.com",
                first_name="Test",
                last_name="User"
            )
            assert profile.email == "valid@example.com"
        except ValidationError:
            pytest.fail("Valid email should not raise ValidationError")
    
    def test_notification_validation(self, mock_redis):
        """Testa validação de notificações"""
        from services.notification_service.main import Notification, NotificationChannel
        from pydantic import ValidationError
        
        # Teste com canal inválido
        with pytest.raises(ValidationError):
            Notification(
                notification_id="test-notification",
                user_id="test-user",
                channel="invalid-channel",
                subject="Test",
                message="Test",
                recipient="test@example.com"
            )
        
        # Teste com dados válidos
        try:
            notification = Notification(
                notification_id="test-notification",
                user_id="test-user",
                channel=NotificationChannel.EMAIL,
                subject="Test",
                message="Test",
                recipient="test@example.com"
            )
            assert notification.channel == NotificationChannel.EMAIL
        except ValidationError:
            pytest.fail("Valid notification should not raise ValidationError")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 