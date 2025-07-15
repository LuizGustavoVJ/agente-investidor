"""
Teste End-to-End para Fase 3 - User Experience Services
Autor: Luiz Gustavo Finotello
"""

import pytest
import requests
import time
import json
from datetime import datetime

class TestFase3Workflow:
    """Teste do workflow completo da Fase 3"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para os testes"""
        self.base_urls = {
            "user_service": "http://localhost:8005",
            "dashboard_service": "http://localhost:8006",
            "notification_service": "http://localhost:8007",
            "report_service": "http://localhost:8008"
        }
        self.test_user_id = "test-user-fase3"
        
        # Aguardar serviços estarem prontos
        self.wait_for_services()
    
    def wait_for_services(self):
        """Aguarda serviços estarem prontos"""
        max_retries = 90  # 90 tentativas
        retry_count = 0
        while retry_count < max_retries:
            try:
                # Verificar se todos os serviços estão respondendo
                for service_name, base_url in self.base_urls.items():
                    response = requests.get(f"{base_url}/health", timeout=5)
                    if response.status_code == 200:
                        print(f"✅ {service_name} está pronto")
                    else:
                        print(f"❌ {service_name} não está respondendo")
                        break
                else:
                    print("🎉 Todos os serviços estão prontos!")
                    return
            except requests.exceptions.RequestException as e:
                print(f"⏳ Aguardando serviços... ({retry_count + 1}/{max_retries})")
                retry_count += 1
                time.sleep(10)  # 90 x 10s = 900s = 15 minutos
        pytest.fail("Serviços não ficaram prontos a tempo")
    
    def test_user_profile_workflow(self):
        """Testa workflow completo de perfil de usuário"""
        print("\n🧪 Testando workflow de perfil de usuário...")
        
        # 1. Criar perfil de usuário
        profile_data = {
            "user_id": self.test_user_id,
            "email": "test@fase3.com",
            "first_name": "Teste",
            "last_name": "Fase3",
            "phone": "+55 11 99999-9999",
            "country": "Brasil",
            "timezone": "America/Sao_Paulo"
        }
        
        response = requests.put(
            f"{self.base_urls['user_service']}/profile/{self.test_user_id}",
            json=profile_data
        )
        
        assert response.status_code == 200
        profile = response.json()
        assert profile["user_id"] == self.test_user_id
        assert profile["email"] == "test@fase3.com"
        print("✅ Perfil criado com sucesso")
        
        # 2. Configurar preferências
        preferences_data = {
            "user_id": self.test_user_id,
            "theme": "dark",
            "notifications_enabled": True,
            "email_notifications": True,
            "push_notifications": True,
            "risk_tolerance": "aggressive",
            "investment_horizon": "long",
            "preferred_currencies": ["BRL", "USD"]
        }
        
        response = requests.put(
            f"{self.base_urls['user_service']}/preferences/{self.test_user_id}",
            json=preferences_data
        )
        
        assert response.status_code == 200
        preferences = response.json()
        assert preferences["theme"] == "dark"
        assert preferences["risk_tolerance"] == "aggressive"
        print("✅ Preferências configuradas")
        
        # 3. Configurar configurações
        settings_data = {
            "user_id": self.test_user_id,
            "privacy_level": "standard",
            "two_factor_auth": True,
            "session_timeout": 7200,
            "max_sessions": 3
        }
        
        response = requests.put(
            f"{self.base_urls['user_service']}/settings/{self.test_user_id}",
            json=settings_data
        )
        
        assert response.status_code == 200
        settings = response.json()
        assert settings["two_factor_auth"] == True
        assert settings["session_timeout"] == 7200
        print("✅ Configurações definidas")
        
        print("🎉 Workflow de perfil de usuário concluído!")
    
    def test_dashboard_workflow(self):
        """Testa workflow completo de dashboard"""
        print("\n🧪 Testando workflow de dashboard...")
        
        # 1. Obter dashboards do usuário
        response = requests.get(
            f"{self.base_urls['dashboard_service']}/dashboards/{self.test_user_id}"
        )
        
        assert response.status_code == 200
        dashboards = response.json()
        assert len(dashboards) > 0
        print("✅ Dashboards obtidos")
        
        # 2. Obter widgets do primeiro dashboard
        dashboard_id = dashboards[0]["dashboard_id"]
        response = requests.get(
            f"{self.base_urls['dashboard_service']}/dashboards/{dashboard_id}/widgets"
        )
        
        assert response.status_code == 200
        widgets = response.json()
        assert len(widgets) > 0
        print("✅ Widgets obtidos")
        
        # 3. Obter métricas do portfólio
        response = requests.get(
            f"{self.base_urls['dashboard_service']}/metrics/portfolio/{self.test_user_id}"
        )
        
        assert response.status_code == 200
        metrics = response.json()
        assert "total_value" in metrics
        assert "total_change_percent" in metrics
        print("✅ Métricas do portfólio obtidas")
        
        # 4. Gerar gráfico de performance
        response = requests.get(
            f"{self.base_urls['dashboard_service']}/charts/portfolio-performance/{self.test_user_id}",
            params={"period": "1y"}
        )
        
        assert response.status_code == 200
        chart_data = response.json()
        assert "labels" in chart_data
        assert "datasets" in chart_data
        print("✅ Gráfico de performance gerado")
        
        # 5. Gerar gráfico de alocação de ativos
        response = requests.get(
            f"{self.base_urls['dashboard_service']}/charts/asset-allocation/{self.test_user_id}"
        )
        
        assert response.status_code == 200
        allocation_data = response.json()
        assert "labels" in allocation_data
        assert "datasets" in allocation_data
        print("✅ Gráfico de alocação gerado")
        
        print("🎉 Workflow de dashboard concluído!")
    
    def test_notification_workflow(self):
        """Testa workflow completo de notificações"""
        print("\n🧪 Testando workflow de notificações...")
        
        # 1. Obter templates de notificação
        response = requests.get(
            f"{self.base_urls['notification_service']}/templates"
        )
        
        assert response.status_code == 200
        templates = response.json()
        assert len(templates) > 0
        print("✅ Templates obtidos")
        
        # 2. Criar notificação
        notification_data = {
            "user_id": self.test_user_id,
            "channel": "email",
            "subject": "Teste Fase 3",
            "message": "Esta é uma notificação de teste da Fase 3",
            "recipient": "test@fase3.com",
            "priority": "normal",
            "metadata": {"test": True}
        }
        
        response = requests.post(
            f"{self.base_urls['notification_service']}/notifications",
            json=notification_data
        )
        
        assert response.status_code == 200
        notification = response.json()
        assert notification["user_id"] == self.test_user_id
        assert notification["subject"] == "Teste Fase 3"
        print("✅ Notificação criada")
        
        # 3. Criar campanha de notificação
        campaign_data = {
            "name": "Campanha Teste Fase 3",
            "description": "Campanha de teste para Fase 3",
            "template_id": templates[0]["template_id"],
            "user_ids": [self.test_user_id],
            "channels": ["email"],
            "priority": "normal"
        }
        
        response = requests.post(
            f"{self.base_urls['notification_service']}/campaigns",
            json=campaign_data
        )
        
        assert response.status_code == 200
        campaign = response.json()
        assert campaign["name"] == "Campanha Teste Fase 3"
        print("✅ Campanha criada")
        
        # 4. Obter notificações do usuário
        response = requests.get(
            f"{self.base_urls['notification_service']}/notifications/{self.test_user_id}",
            params={"limit": 10}
        )
        
        assert response.status_code == 200
        notifications = response.json()
        assert len(notifications) >= 1
        print("✅ Notificações do usuário obtidas")
        
        print("🎉 Workflow de notificações concluído!")
    
    def test_report_workflow(self):
        """Testa workflow completo de relatórios"""
        print("\n🧪 Testando workflow de relatórios...")
        
        # 1. Obter templates de relatório
        response = requests.get(
            f"{self.base_urls['report_service']}/templates"
        )
        
        assert response.status_code == 200
        templates = response.json()
        assert len(templates) > 0
        print("✅ Templates de relatório obtidos")
        
        # 2. Criar relatório de portfólio
        report_request = {
            "user_id": self.test_user_id,
            "report_type": "portfolio_summary",
            "format": "pdf",
            "parameters": {"period": "1y"},
            "include_charts": True,
            "include_tables": True,
            "custom_title": "Relatório de Teste Fase 3",
            "custom_description": "Relatório gerado durante teste da Fase 3"
        }
        
        response = requests.post(
            f"{self.base_urls['report_service']}/reports",
            json=report_request
        )
        
        assert response.status_code == 200
        report = response.json()
        assert report["user_id"] == self.test_user_id
        assert report["report_type"] == "portfolio_summary"
        assert report["format"] == "pdf"
        print("✅ Relatório criado")
        
        # 3. Aguardar geração do relatório
        report_id = report["report_id"]
        max_wait = 60  # 60 segundos
        wait_time = 0
        
        while wait_time < max_wait:
            response = requests.get(
                f"{self.base_urls['report_service']}/reports/{report_id}"
            )
            
            if response.status_code == 200:
                report_status = response.json()
                if report_status["status"] == "completed":
                    print("✅ Relatório gerado com sucesso")
                    break
                elif report_status["status"] == "failed":
                    pytest.fail("Relatório falhou na geração")
            
            time.sleep(2)
            wait_time += 2
        
        if wait_time >= max_wait:
            pytest.fail("Timeout aguardando geração do relatório")
        
        # 4. Baixar relatório
        response = requests.get(
            f"{self.base_urls['report_service']}/reports/{report_id}/download"
        )
        
        assert response.status_code == 200
        assert len(response.content) > 0
        print("✅ Relatório baixado com sucesso")
        
        # 5. Obter relatórios do usuário
        response = requests.get(
            f"{self.base_urls['report_service']}/reports/user/{self.test_user_id}"
        )
        
        assert response.status_code == 200
        user_reports = response.json()
        assert len(user_reports) >= 1
        print("✅ Relatórios do usuário obtidos")
        
        print("🎉 Workflow de relatórios concluído!")
    
    def test_integrated_workflow(self):
        """Testa workflow integrado entre todos os serviços"""
        print("\n🧪 Testando workflow integrado...")
        
        # 1. Criar perfil completo
        profile_data = {
            "user_id": f"{self.test_user_id}-integrated",
            "email": "integrated@fase3.com",
            "first_name": "Integrated",
            "last_name": "Test",
            "phone": "+55 11 88888-8888",
            "country": "Brasil"
        }
        
        response = requests.put(
            f"{self.base_urls['user_service']}/profile/{profile_data['user_id']}",
            json=profile_data
        )
        assert response.status_code == 200
        
        # 2. Configurar preferências para dashboard
        preferences_data = {
            "user_id": profile_data["user_id"],
            "theme": "dark",
            "dashboard_layout": {"widgets": [], "columns": 3, "rows": 4},
            "default_methodologies": ["warren_buffett", "benjamin_graham"],
            "risk_tolerance": "moderate"
        }
        
        response = requests.put(
            f"{self.base_urls['user_service']}/preferences/{profile_data['user_id']}",
            json=preferences_data
        )
        assert response.status_code == 200
        
        # 3. Obter dashboard personalizado
        response = requests.get(
            f"{self.base_urls['dashboard_service']}/dashboards/{profile_data['user_id']}"
        )
        assert response.status_code == 200
        
        # 4. Criar notificação sobre dashboard
        notification_data = {
            "user_id": profile_data["user_id"],
            "channel": "email",
            "subject": "Dashboard Personalizado Criado",
            "message": "Seu dashboard personalizado foi configurado com sucesso!",
            "recipient": profile_data["email"],
            "priority": "normal"
        }
        
        response = requests.post(
            f"{self.base_urls['notification_service']}/notifications",
            json=notification_data
        )
        assert response.status_code == 200
        
        # 5. Gerar relatório do dashboard
        report_request = {
            "user_id": profile_data["user_id"],
            "report_type": "portfolio_summary",
            "format": "pdf",
            "parameters": {"period": "6m"},
            "include_charts": True,
            "include_tables": True,
            "custom_title": "Relatório Integrado Fase 3"
        }
        
        response = requests.post(
            f"{self.base_urls['report_service']}/reports",
            json=report_request
        )
        assert response.status_code == 200
        
        # 6. Verificar atividade do usuário
        response = requests.get(
            f"{self.base_urls['user_service']}/activity/{profile_data['user_id']}",
            params={"limit": 10}
        )
        assert response.status_code == 200
        
        print("🎉 Workflow integrado concluído com sucesso!")
    
    def test_error_handling(self):
        """Testa tratamento de erros"""
        print("\n🧪 Testando tratamento de erros...")
        
        # 1. Tentar acessar usuário inexistente
        response = requests.get(
            f"{self.base_urls['user_service']}/profile/non-existent-user"
        )
        assert response.status_code == 200  # Retorna dados padrão
        
        # 2. Tentar criar notificação com dados inválidos
        invalid_notification = {
            "user_id": "test-user",
            "channel": "invalid-channel",
            "subject": "Test",
            "message": "Test",
            "recipient": "invalid-email"
        }
        
        response = requests.post(
            f"{self.base_urls['notification_service']}/notifications",
            json=invalid_notification
        )
        # Deve retornar erro de validação
        assert response.status_code in [400, 422]
        
        # 3. Tentar gerar relatório com formato inválido
        invalid_report = {
            "user_id": "test-user",
            "report_type": "invalid_type",
            "format": "invalid_format",
            "parameters": {}
        }
        
        response = requests.post(
            f"{self.base_urls['report_service']}/reports",
            json=invalid_report
        )
        # Deve retornar erro de validação
        assert response.status_code in [400, 422]
        
        print("✅ Tratamento de erros funcionando corretamente")
    
    def test_performance_metrics(self):
        """Testa métricas de performance"""
        print("\n🧪 Testando métricas de performance...")
        
        # 1. Testar tempo de resposta do User Service
        start_time = time.time()
        response = requests.get(
            f"{self.base_urls['user_service']}/profile/{self.test_user_id}"
        )
        user_service_time = time.time() - start_time
        
        assert response.status_code == 200
        assert user_service_time < 2.0  # Deve responder em menos de 2 segundos
        print(f"✅ User Service: {user_service_time:.3f}s")
        
        # 2. Testar tempo de resposta do Dashboard Service
        start_time = time.time()
        response = requests.get(
            f"{self.base_urls['dashboard_service']}/dashboards/{self.test_user_id}"
        )
        dashboard_service_time = time.time() - start_time
        
        assert response.status_code == 200
        assert dashboard_service_time < 2.0
        print(f"✅ Dashboard Service: {dashboard_service_time:.3f}s")
        
        # 3. Testar tempo de resposta do Notification Service
        start_time = time.time()
        response = requests.get(
            f"{self.base_urls['notification_service']}/templates"
        )
        notification_service_time = time.time() - start_time
        
        assert response.status_code == 200
        assert notification_service_time < 2.0
        print(f"✅ Notification Service: {notification_service_time:.3f}s")
        
        # 4. Testar tempo de resposta do Report Service
        start_time = time.time()
        response = requests.get(
            f"{self.base_urls['report_service']}/templates"
        )
        report_service_time = time.time() - start_time
        
        assert response.status_code == 200
        assert report_service_time < 2.0
        print(f"✅ Report Service: {report_service_time:.3f}s")
        
        print("🎉 Todas as métricas de performance estão dentro do esperado!")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"]) 