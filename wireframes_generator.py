import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

class WireframeGenerator:
    def __init__(self):
        self.fig_width = 11.69  # A4 width in inches
        self.fig_height = 8.27  # A4 height in inches
        self.colors = {
            'bg': '#f8f9fa',
            'primary': '#667eea',
            'secondary': '#764ba2',
            'text': '#333333',
            'border': '#e0e0e0',
            'success': '#28a745',
            'warning': '#ffc107',
            'danger': '#dc3545'
        }
    
    def create_wireframe_base(self, title):
        """Create base wireframe structure"""
        fig, ax = plt.subplots(figsize=(self.fig_width, self.fig_height))
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Background
        bg_rect = patches.Rectangle((0, 0), 100, 100, 
                                  linewidth=2, edgecolor=self.colors['border'], 
                                  facecolor=self.colors['bg'])
        ax.add_patch(bg_rect)
        
        # Title
        ax.text(50, 95, title, ha='center', va='center', 
                fontsize=16, fontweight='bold', color=self.colors['text'])
        
        return fig, ax
    
    def add_header(self, ax, has_user_menu=False):
        """Add header with navigation"""
        # Header background
        header_rect = patches.Rectangle((5, 85), 90, 8, 
                                      linewidth=1, edgecolor=self.colors['border'], 
                                      facecolor=self.colors['primary'], alpha=0.1)
        ax.add_patch(header_rect)
        
        # Logo
        ax.text(10, 89, "📈 Agente Investidor", ha='left', va='center', 
                fontsize=12, fontweight='bold', color=self.colors['primary'])
        
        # Navigation menu
        nav_items = ["Home", "Dashboard", "Análise", "Chat", "Metodologias"]
        for i, item in enumerate(nav_items):
            x_pos = 25 + (i * 12)
            nav_rect = patches.Rectangle((x_pos-1, 87), 10, 4, 
                                       linewidth=1, edgecolor=self.colors['border'], 
                                       facecolor='white', alpha=0.8)
            ax.add_patch(nav_rect)
            ax.text(x_pos + 4, 89, item, ha='center', va='center', 
                    fontsize=9, color=self.colors['text'])
        
        # User menu (if applicable)
        if has_user_menu:
            user_rect = patches.Rectangle((85, 87), 10, 4, 
                                        linewidth=1, edgecolor=self.colors['border'], 
                                        facecolor=self.colors['secondary'], alpha=0.2)
            ax.add_patch(user_rect)
            ax.text(90, 89, "👤 User", ha='center', va='center', 
                    fontsize=9, color=self.colors['text'])
    
    def add_form_field(self, ax, x, y, width, height, label, placeholder=""):
        """Add form field with label"""
        # Label
        ax.text(x, y + height + 2, label, ha='left', va='bottom', 
                fontsize=10, color=self.colors['text'])
        
        # Field
        field_rect = patches.Rectangle((x, y), width, height, 
                                     linewidth=1, edgecolor=self.colors['border'], 
                                     facecolor='white')
        ax.add_patch(field_rect)
        
        # Placeholder
        if placeholder:
            ax.text(x + 1, y + height/2, placeholder, ha='left', va='center', 
                    fontsize=9, color='gray', alpha=0.7)
    
    def add_button(self, ax, x, y, width, height, text, style='primary'):
        """Add button with text"""
        color = self.colors['primary'] if style == 'primary' else self.colors['secondary']
        
        button_rect = patches.Rectangle((x, y), width, height, 
                                      linewidth=1, edgecolor=color, 
                                      facecolor=color, alpha=0.8)
        ax.add_patch(button_rect)
        
        ax.text(x + width/2, y + height/2, text, ha='center', va='center', 
                fontsize=10, color='white', fontweight='bold')
    
    def add_chart_placeholder(self, ax, x, y, width, height, title):
        """Add chart placeholder"""
        # Chart container
        chart_rect = patches.Rectangle((x, y), width, height, 
                                     linewidth=1, edgecolor=self.colors['border'], 
                                     facecolor='white')
        ax.add_patch(chart_rect)
        
        # Chart title
        ax.text(x + width/2, y + height - 2, title, ha='center', va='center', 
                fontsize=10, fontweight='bold', color=self.colors['text'])
        
        # Chart placeholder
        ax.text(x + width/2, y + height/2, "📊 Gráfico", ha='center', va='center', 
                fontsize=12, color=self.colors['primary'], alpha=0.7)
    
    def add_table_placeholder(self, ax, x, y, width, height, title, columns):
        """Add table placeholder"""
        # Table container
        table_rect = patches.Rectangle((x, y), width, height, 
                                     linewidth=1, edgecolor=self.colors['border'], 
                                     facecolor='white')
        ax.add_patch(table_rect)
        
        # Table title
        ax.text(x + width/2, y + height - 2, title, ha='center', va='center', 
                fontsize=10, fontweight='bold', color=self.colors['text'])
        
        # Table headers
        header_height = 3
        header_rect = patches.Rectangle((x, y + height - 5), width, header_height, 
                                      linewidth=1, edgecolor=self.colors['border'], 
                                      facecolor=self.colors['primary'], alpha=0.1)
        ax.add_patch(header_rect)
        
        # Column headers
        col_width = width / len(columns)
        for i, col in enumerate(columns):
            col_x = x + (i * col_width)
            ax.text(col_x + col_width/2, y + height - 3.5, col, ha='center', va='center', 
                    fontsize=8, fontweight='bold', color=self.colors['text'])
    
    def generate_login_wireframe(self):
        """Generate login screen wireframe"""
        fig, ax = self.create_wireframe_base("WIREFRAME - Tela de Login")
        
        # Centered login form
        form_width = 30
        form_height = 35
        form_x = (100 - form_width) / 2
        form_y = (100 - form_height) / 2
        
        # Form container
        form_rect = patches.Rectangle((form_x, form_y), form_width, form_height, 
                                    linewidth=2, edgecolor=self.colors['border'], 
                                    facecolor='white')
        ax.add_patch(form_rect)
        
        # Form title
        ax.text(50, form_y + form_height - 5, "Entrar", ha='center', va='center', 
                fontsize=18, fontweight='bold', color=self.colors['primary'])
        
        # Form fields
        field_y = form_y + form_height - 15
        self.add_form_field(ax, form_x + 3, field_y, form_width - 6, 4, "Usuário", "Digite seu usuário")
        
        field_y -= 8
        self.add_form_field(ax, form_x + 3, field_y, form_width - 6, 4, "Senha", "Digite sua senha")
        
        # Login button
        button_y = field_y - 8
        self.add_button(ax, form_x + 3, button_y, form_width - 6, 5, "Entrar", 'primary')
        
        # Links
        ax.text(50, button_y - 5, "Não tem conta? Cadastre-se", ha='center', va='center', 
                fontsize=9, color=self.colors['primary'])
        
        # Logo/Brand
        ax.text(50, 85, "📈 Agente Investidor", ha='center', va='center', 
                fontsize=16, fontweight='bold', color=self.colors['primary'])
        
        return fig
    
    def generate_register_wireframe(self):
        """Generate register screen wireframe"""
        fig, ax = self.create_wireframe_base("WIREFRAME - Tela de Cadastro")
        
        # Centered register form
        form_width = 30
        form_height = 40
        form_x = (100 - form_width) / 2
        form_y = (100 - form_height) / 2
        
        # Form container
        form_rect = patches.Rectangle((form_x, form_y), form_width, form_height, 
                                    linewidth=2, edgecolor=self.colors['border'], 
                                    facecolor='white')
        ax.add_patch(form_rect)
        
        # Form title
        ax.text(50, form_y + form_height - 5, "Cadastro", ha='center', va='center', 
                fontsize=18, fontweight='bold', color=self.colors['primary'])
        
        # Form fields
        field_y = form_y + form_height - 15
        self.add_form_field(ax, form_x + 3, field_y, form_width - 6, 4, "Usuário", "Digite seu usuário")
        
        field_y -= 8
        self.add_form_field(ax, form_x + 3, field_y, form_width - 6, 4, "E-mail", "Digite seu e-mail")
        
        field_y -= 8
        self.add_form_field(ax, form_x + 3, field_y, form_width - 6, 4, "Senha", "Digite sua senha")
        
        # Register button
        button_y = field_y - 8
        self.add_button(ax, form_x + 3, button_y, form_width - 6, 5, "Cadastrar", 'primary')
        
        # Links
        ax.text(50, button_y - 5, "Já tem conta? Entrar", ha='center', va='center', 
                fontsize=9, color=self.colors['primary'])
        
        # Logo/Brand
        ax.text(50, 85, "📈 Agente Investidor", ha='center', va='center', 
                fontsize=16, fontweight='bold', color=self.colors['primary'])
        
        return fig
    
    def generate_home_wireframe(self):
        """Generate home screen wireframe"""
        fig, ax = self.create_wireframe_base("WIREFRAME - Tela Home")
        
        # Header
        self.add_header(ax, has_user_menu=True)
        
        # Hero section
        hero_rect = patches.Rectangle((5, 55), 90, 25, 
                                    linewidth=1, edgecolor=self.colors['border'], 
                                    facecolor=self.colors['primary'], alpha=0.05)
        ax.add_patch(hero_rect)
        
        # Hero content
        ax.text(30, 72, "Seu Mentor Pessoal em", ha='center', va='center', 
                fontsize=14, color=self.colors['text'])
        ax.text(30, 68, "INVESTIMENTOS", ha='center', va='center', 
                fontsize=16, fontweight='bold', color=self.colors['primary'])
        
        # Hero description
        ax.text(30, 63, "Baseado nas metodologias dos maiores", ha='center', va='center', 
                fontsize=10, color=self.colors['text'])
        ax.text(30, 60, "investidores do mundo", ha='center', va='center', 
                fontsize=10, color=self.colors['text'])
        
        # Hero buttons
        self.add_button(ax, 20, 57, 12, 4, "Analisar Ação", 'primary')
        self.add_button(ax, 35, 57, 12, 4, "Chat com Agente", 'secondary')
        
        # Hero stats
        stat_x = 65
        for i, stat in enumerate(["10 Metodologias", "50+ Indicadores", "Dados Tempo Real"]):
            stat_y = 75 - (i * 8)
            stat_rect = patches.Rectangle((stat_x, stat_y), 25, 6, 
                                        linewidth=1, edgecolor=self.colors['border'], 
                                        facecolor='white', alpha=0.9)
            ax.add_patch(stat_rect)
            ax.text(stat_x + 12.5, stat_y + 3, stat, ha='center', va='center', 
                    fontsize=10, fontweight='bold', color=self.colors['text'])
        
        # Investors section
        ax.text(50, 50, "Baseado nos Maiores Investidores", ha='center', va='center', 
                fontsize=14, fontweight='bold', color=self.colors['text'])
        
        # Investor cards
        investors = ["Warren Buffett", "Benjamin Graham", "Peter Lynch", "Dividend Focus"]
        for i, investor in enumerate(investors):
            card_x = 10 + (i * 20)
            card_rect = patches.Rectangle((card_x, 35), 18, 12, 
                                        linewidth=1, edgecolor=self.colors['border'], 
                                        facecolor='white')
            ax.add_patch(card_rect)
            
            # Investor avatar
            avatar_circle = patches.Circle((card_x + 9, 43), 3, 
                                         linewidth=1, edgecolor=self.colors['border'], 
                                         facecolor=self.colors['primary'], alpha=0.2)
            ax.add_patch(avatar_circle)
            ax.text(card_x + 9, 43, "👤", ha='center', va='center', fontsize=12)
            
            # Investor name
            ax.text(card_x + 9, 38, investor, ha='center', va='center', 
                    fontsize=9, fontweight='bold', color=self.colors['text'])
        
        # Footer
        footer_rect = patches.Rectangle((5, 5), 90, 8, 
                                      linewidth=1, edgecolor=self.colors['border'], 
                                      facecolor=self.colors['primary'], alpha=0.05)
        ax.add_patch(footer_rect)
        ax.text(50, 9, "© 2025 Agente Investidor - Desenvolvido por Luiz Gustavo Finotello", 
                ha='center', va='center', fontsize=9, color=self.colors['text'])
        
        return fig
    
    def generate_dashboard_wireframe(self):
        """Generate dashboard screen wireframe"""
        fig, ax = self.create_wireframe_base("WIREFRAME - Dashboard do Mercado")
        
        # Header
        self.add_header(ax, has_user_menu=True)
        
        # Page title
        ax.text(50, 80, "Dashboard do Mercado", ha='center', va='center', 
                fontsize=16, fontweight='bold', color=self.colors['text'])
        
        # Top charts row
        self.add_chart_placeholder(ax, 5, 60, 43, 15, "Ibovespa - Últimos 30 dias")
        self.add_chart_placeholder(ax, 52, 60, 43, 15, "Setores em Destaque")
        
        # Middle charts row
        self.add_chart_placeholder(ax, 5, 40, 43, 15, "Top Ações - Maiores Altas")
        self.add_chart_placeholder(ax, 52, 40, 43, 15, "Análise de Volatilidade")
        
        # Featured stocks table
        self.add_table_placeholder(ax, 5, 20, 90, 15, "Ações em Destaque", 
                                  ["Ação", "Preço", "Variação", "Volume", "P/E", "Score"])
        
        # Economic indicators
        ax.text(50, 15, "Indicadores Econômicos", ha='center', va='center', 
                fontsize=12, fontweight='bold', color=self.colors['text'])
        
        indicators = ["IPCA", "PIB", "Desemprego", "Commodities"]
        for i, indicator in enumerate(indicators):
            ind_x = 15 + (i * 20)
            ind_rect = patches.Rectangle((ind_x, 8), 15, 6, 
                                       linewidth=1, edgecolor=self.colors['border'], 
                                       facecolor='white')
            ax.add_patch(ind_rect)
            ax.text(ind_x + 7.5, 11, indicator, ha='center', va='center', 
                    fontsize=9, fontweight='bold', color=self.colors['text'])
        
        return fig
    
    def generate_analysis_wireframe(self):
        """Generate stock analysis screen wireframe"""
        fig, ax = self.create_wireframe_base("WIREFRAME - Análise de Ações")
        
        # Header
        self.add_header(ax, has_user_menu=True)
        
        # Page title
        ax.text(50, 80, "Análise de Ações", ha='center', va='center', 
                fontsize=16, fontweight='bold', color=self.colors['text'])
        
        # Analysis form
        form_rect = patches.Rectangle((5, 60), 90, 15, 
                                    linewidth=1, edgecolor=self.colors['border'], 
                                    facecolor='white')
        ax.add_patch(form_rect)
        
        # Form fields
        self.add_form_field(ax, 10, 67, 30, 4, "Selecione a Ação", "Ex: PETR4, VALE3")
        self.add_form_field(ax, 45, 67, 30, 4, "Metodologia", "Warren Buffett")
        self.add_button(ax, 80, 67, 12, 4, "Analisar", 'primary')
        
        # Results section
        results_rect = patches.Rectangle((5, 20), 90, 35, 
                                       linewidth=1, edgecolor=self.colors['border'], 
                                       facecolor='white')
        ax.add_patch(results_rect)
        
        # Results header
        ax.text(50, 52, "Resultados da Análise", ha='center', va='center', 
                fontsize=14, fontweight='bold', color=self.colors['text'])
        
        # Score display
        score_circle = patches.Circle((20, 45), 8, 
                                    linewidth=2, edgecolor=self.colors['primary'], 
                                    facecolor=self.colors['primary'], alpha=0.1)
        ax.add_patch(score_circle)
        ax.text(20, 45, "85", ha='center', va='center', 
                fontsize=20, fontweight='bold', color=self.colors['primary'])
        ax.text(20, 40, "Score", ha='center', va='center', 
                fontsize=10, color=self.colors['text'])
        
        # Recommendation
        rec_rect = patches.Rectangle((35, 42), 25, 8, 
                                   linewidth=1, edgecolor=self.colors['success'], 
                                   facecolor=self.colors['success'], alpha=0.1)
        ax.add_patch(rec_rect)
        ax.text(47.5, 46, "COMPRA", ha='center', va='center', 
                fontsize=14, fontweight='bold', color=self.colors['success'])
        
        # Details
        ax.text(70, 48, "Pontos Fortes:", ha='left', va='center', 
                fontsize=10, fontweight='bold', color=self.colors['text'])
        ax.text(70, 45, "• ROE > 15%", ha='left', va='center', 
                fontsize=9, color=self.colors['text'])
        ax.text(70, 42, "• P/E < 20", ha='left', va='center', 
                fontsize=9, color=self.colors['text'])
        
        # Charts section
        self.add_chart_placeholder(ax, 10, 25, 35, 12, "Histórico de Preços")
        self.add_chart_placeholder(ax, 55, 25, 35, 12, "Indicadores Técnicos")
        
        return fig
    
    def generate_chat_wireframe(self):
        """Generate chat screen wireframe"""
        fig, ax = self.create_wireframe_base("WIREFRAME - Chat com Agente")
        
        # Header
        self.add_header(ax, has_user_menu=True)
        
        # Page title
        ax.text(50, 80, "Chat com o Agente Investidor", ha='center', va='center', 
                fontsize=16, fontweight='bold', color=self.colors['text'])
        
        # Chat container
        chat_rect = patches.Rectangle((5, 15), 90, 60, 
                                    linewidth=1, edgecolor=self.colors['border'], 
                                    facecolor='white')
        ax.add_patch(chat_rect)
        
        # Chat messages
        # Agent message
        agent_msg_rect = patches.Rectangle((10, 60), 60, 8, 
                                         linewidth=1, edgecolor=self.colors['border'], 
                                         facecolor=self.colors['primary'], alpha=0.1)
        ax.add_patch(agent_msg_rect)
        ax.text(12, 66, "🤖 Agente", ha='left', va='center', 
                fontsize=9, fontweight='bold', color=self.colors['primary'])
        ax.text(12, 62, "Olá! Como posso ajudá-lo com seus investimentos?", ha='left', va='center', 
                fontsize=10, color=self.colors['text'])
        
        # User message
        user_msg_rect = patches.Rectangle((25, 48), 60, 8, 
                                        linewidth=1, edgecolor=self.colors['border'], 
                                        facecolor=self.colors['secondary'], alpha=0.1)
        ax.add_patch(user_msg_rect)
        ax.text(83, 54, "👤 Você", ha='right', va='center', 
                fontsize=9, fontweight='bold', color=self.colors['secondary'])
        ax.text(83, 50, "Como Warren Buffett analisa ações?", ha='right', va='center', 
                fontsize=10, color=self.colors['text'])
        
        # Agent response
        agent_resp_rect = patches.Rectangle((10, 30), 70, 15, 
                                          linewidth=1, edgecolor=self.colors['border'], 
                                          facecolor=self.colors['primary'], alpha=0.1)
        ax.add_patch(agent_resp_rect)
        ax.text(12, 42, "🤖 Agente", ha='left', va='center', 
                fontsize=9, fontweight='bold', color=self.colors['primary'])
        ax.text(12, 38, "Warren Buffett usa Value Investing, focando em:", ha='left', va='center', 
                fontsize=10, color=self.colors['text'])
        ax.text(12, 35, "• Empresas com vantagem competitiva", ha='left', va='center', 
                fontsize=9, color=self.colors['text'])
        ax.text(12, 32, "• Gestão de qualidade e preço razoável", ha='left', va='center', 
                fontsize=9, color=self.colors['text'])
        
        # Suggestion buttons
        ax.text(50, 25, "Sugestões:", ha='center', va='center', 
                fontsize=10, fontweight='bold', color=self.colors['text'])
        
        suggestions = ["O que é P/E?", "Como começar?", "Análise técnica"]
        for i, suggestion in enumerate(suggestions):
            btn_x = 15 + (i * 25)
            self.add_button(ax, btn_x, 20, 20, 3, suggestion, 'secondary')
        
        # Input area
        input_rect = patches.Rectangle((10, 16), 70, 4, 
                                     linewidth=1, edgecolor=self.colors['border'], 
                                     facecolor='white')
        ax.add_patch(input_rect)
        ax.text(12, 18, "Digite sua pergunta...", ha='left', va='center', 
                fontsize=9, color='gray', alpha=0.7)
        
        # Send button
        self.add_button(ax, 82, 16, 10, 4, "Enviar", 'primary')
        
        return fig
    
    def generate_methodologies_wireframe(self):
        """Generate methodologies screen wireframe"""
        fig, ax = self.create_wireframe_base("WIREFRAME - Metodologias de Investimento")
        
        # Header
        self.add_header(ax, has_user_menu=True)
        
        # Page title
        ax.text(50, 80, "Metodologias de Investimento", ha='center', va='center', 
                fontsize=16, fontweight='bold', color=self.colors['text'])
        
        # Methodology cards
        methodologies = [
            ("Warren Buffett", "Value Investing", ["P/E < 25", "ROE > 15%", "D/E < 0.5"]),
            ("Benjamin Graham", "Defensive Value", ["P/E < 15", "P/B < 1.5", "Current Ratio > 2"]),
            ("Peter Lynch", "Growth at Reasonable Price", ["PEG < 1", "Crescimento > 15%", "Small Caps"]),
            ("Foco em Dividendos", "Income Investing", ["DY > 4%", "Payout < 80%", "ROE > 12%"])
        ]
        
        for i, (name, type_inv, indicators) in enumerate(methodologies):
            row = i // 2
            col = i % 2
            
            card_x = 10 + (col * 45)
            card_y = 55 - (row * 25)
            
            # Card container
            card_rect = patches.Rectangle((card_x, card_y), 40, 20, 
                                        linewidth=1, edgecolor=self.colors['border'], 
                                        facecolor='white')
            ax.add_patch(card_rect)
            
            # Card header
            header_rect = patches.Rectangle((card_x, card_y + 15), 40, 5, 
                                          linewidth=1, edgecolor=self.colors['border'], 
                                          facecolor=self.colors['primary'], alpha=0.1)
            ax.add_patch(header_rect)
            
            # Methodology name
            ax.text(card_x + 20, card_y + 17.5, name, ha='center', va='center', 
                    fontsize=11, fontweight='bold', color=self.colors['text'])
            
            # Type
            ax.text(card_x + 20, card_y + 12, type_inv, ha='center', va='center', 
                    fontsize=9, color=self.colors['primary'])
            
            # Indicators
            for j, indicator in enumerate(indicators):
                ind_y = card_y + 9 - (j * 2.5)
                ind_rect = patches.Rectangle((card_x + 2, ind_y - 0.5), 36, 2, 
                                           linewidth=1, edgecolor=self.colors['border'], 
                                           facecolor=self.colors['success'], alpha=0.1)
                ax.add_patch(ind_rect)
                ax.text(card_x + 20, ind_y, indicator, ha='center', va='center', 
                        fontsize=8, color=self.colors['text'])
        
        return fig
    
    def generate_profile_wireframe(self):
        """Generate investor profile screen wireframe"""
        fig, ax = self.create_wireframe_base("WIREFRAME - Perfil do Investidor")
        
        # Header
        self.add_header(ax, has_user_menu=True)
        
        # Modal overlay
        overlay_rect = patches.Rectangle((0, 0), 100, 100, 
                                       linewidth=0, edgecolor='none', 
                                       facecolor='black', alpha=0.3)
        ax.add_patch(overlay_rect)
        
        # Modal container
        modal_width = 60
        modal_height = 50
        modal_x = (100 - modal_width) / 2
        modal_y = (100 - modal_height) / 2
        
        modal_rect = patches.Rectangle((modal_x, modal_y), modal_width, modal_height, 
                                     linewidth=2, edgecolor=self.colors['border'], 
                                     facecolor='white')
        ax.add_patch(modal_rect)
        
        # Modal header
        ax.text(50, modal_y + modal_height - 5, "Perfil de Investidor", ha='center', va='center', 
                fontsize=16, fontweight='bold', color=self.colors['text'])
        
        # Close button
        close_rect = patches.Rectangle((modal_x + modal_width - 5, modal_y + modal_height - 5), 3, 3, 
                                     linewidth=1, edgecolor=self.colors['border'], 
                                     facecolor=self.colors['danger'], alpha=0.2)
        ax.add_patch(close_rect)
        ax.text(modal_x + modal_width - 3.5, modal_y + modal_height - 3.5, "×", ha='center', va='center', 
                fontsize=16, color=self.colors['danger'])
        
        # Question
        ax.text(50, modal_y + modal_height - 12, "Qual é o seu principal objetivo com investimentos?", 
                ha='center', va='center', fontsize=12, color=self.colors['text'])
        
        # Answer options
        options = [
            "Preservar capital e ter segurança",
            "Renda passiva através de dividendos",
            "Crescimento de longo prazo",
            "Ganhos rápidos e especulação"
        ]
        
        for i, option in enumerate(options):
            option_y = modal_y + modal_height - 20 - (i * 6)
            option_rect = patches.Rectangle((modal_x + 5, option_y), modal_width - 10, 4, 
                                          linewidth=1, edgecolor=self.colors['border'], 
                                          facecolor='white')
            ax.add_patch(option_rect)
            
            # Radio button
            radio_circle = patches.Circle((modal_x + 8, option_y + 2), 1, 
                                        linewidth=1, edgecolor=self.colors['border'], 
                                        facecolor='white')
            ax.add_patch(radio_circle)
            
            # Option text
            ax.text(modal_x + 12, option_y + 2, option, ha='left', va='center', 
                    fontsize=10, color=self.colors['text'])
        
        # Navigation buttons
        self.add_button(ax, modal_x + 5, modal_y + 5, 12, 4, "Anterior", 'secondary')
        self.add_button(ax, modal_x + modal_width - 17, modal_y + 5, 12, 4, "Próximo", 'primary')
        
        return fig
    
    def generate_detailed_results_wireframe(self):
        """Generate detailed analysis results screen wireframe"""
        fig, ax = self.create_wireframe_base("WIREFRAME - Resultados Detalhados da Análise")
        
        # Header
        self.add_header(ax, has_user_menu=True)
        
        # Page title
        ax.text(50, 80, "Análise Detalhada - PETR4", ha='center', va='center', 
                fontsize=16, fontweight='bold', color=self.colors['text'])
        
        # Score section
        score_rect = patches.Rectangle((5, 70), 25, 8, 
                                     linewidth=1, edgecolor=self.colors['border'], 
                                     facecolor=self.colors['primary'], alpha=0.1)
        ax.add_patch(score_rect)
        ax.text(17.5, 76, "Score: 85", ha='center', va='center', 
                fontsize=14, fontweight='bold', color=self.colors['primary'])
        ax.text(17.5, 72, "COMPRA", ha='center', va='center', 
                fontsize=12, fontweight='bold', color=self.colors['success'])
        
        # Price info
        price_rect = patches.Rectangle((35, 70), 25, 8, 
                                     linewidth=1, edgecolor=self.colors['border'], 
                                     facecolor='white')
        ax.add_patch(price_rect)
        ax.text(47.5, 76, "Preço Atual: R$ 32,45", ha='center', va='center', 
                fontsize=10, color=self.colors['text'])
        ax.text(47.5, 72, "Preço Alvo: R$ 42,00", ha='center', va='center', 
                fontsize=10, color=self.colors['success'])
        
        # Methodology
        method_rect = patches.Rectangle((65, 70), 30, 8, 
                                      linewidth=1, edgecolor=self.colors['border'], 
                                      facecolor='white')
        ax.add_patch(method_rect)
        ax.text(80, 74, "Metodologia: Warren Buffett", ha='center', va='center', 
                fontsize=10, fontweight='bold', color=self.colors['text'])
        
        # Charts section
        self.add_chart_placeholder(ax, 5, 45, 43, 20, "Histórico de Preços (6 meses)")
        self.add_chart_placeholder(ax, 52, 45, 43, 20, "Volume de Negociação")
        
        # Detailed metrics
        metrics_rect = patches.Rectangle((5, 20), 90, 20, 
                                       linewidth=1, edgecolor=self.colors['border'], 
                                       facecolor='white')
        ax.add_patch(metrics_rect)
        
        ax.text(50, 37, "Métricas Detalhadas", ha='center', va='center', 
                fontsize=14, fontweight='bold', color=self.colors['text'])
        
        # Metric categories
        categories = [
            ("Valuation", ["P/E: 12.5", "P/B: 1.8", "EV/EBITDA: 8.2"]),
            ("Rentabilidade", ["ROE: 18%", "ROA: 8%", "ROIC: 12%"]),
            ("Endividamento", ["D/E: 0.3", "Current Ratio: 2.1", "Quick Ratio: 1.5"]),
            ("Crescimento", ["Receita: 15%", "Lucro: 22%", "Dividend Yield: 8%"])
        ]
        
        for i, (category, metrics) in enumerate(categories):
            cat_x = 10 + (i * 20)
            
            # Category header
            ax.text(cat_x + 10, 32, category, ha='center', va='center', 
                    fontsize=10, fontweight='bold', color=self.colors['text'])
            
            # Metrics
            for j, metric in enumerate(metrics):
                metric_y = 29 - (j * 2)
                ax.text(cat_x + 10, metric_y, metric, ha='center', va='center', 
                        fontsize=8, color=self.colors['text'])
        
        # Justification
        just_rect = patches.Rectangle((5, 5), 90, 10, 
                                    linewidth=1, edgecolor=self.colors['border'], 
                                    facecolor=self.colors['primary'], alpha=0.05)
        ax.add_patch(just_rect)
        
        ax.text(50, 12, "Justificativa da Análise", ha='center', va='center', 
                fontsize=12, fontweight='bold', color=self.colors['text'])
        ax.text(50, 8, "A empresa apresenta fundamentos sólidos com ROE acima de 15%, P/E atrativo", 
                ha='center', va='center', fontsize=9, color=self.colors['text'])
        ax.text(50, 6, "e baixo endividamento, seguindo os critérios de Warren Buffett.", 
                ha='center', va='center', fontsize=9, color=self.colors['text'])
        
        return fig
    
    def generate_all_wireframes(self, filename="wireframes_agente_investidor.pdf"):
        """Generate all wireframes and save to PDF"""
        with PdfPages(filename) as pdf:
            # Generate all wireframes
            wireframes = [
                ("Tela de Login", self.generate_login_wireframe()),
                ("Tela de Cadastro", self.generate_register_wireframe()),
                ("Tela Home", self.generate_home_wireframe()),
                ("Dashboard", self.generate_dashboard_wireframe()),
                ("Análise de Ações", self.generate_analysis_wireframe()),
                ("Chat", self.generate_chat_wireframe()),
                ("Metodologias", self.generate_methodologies_wireframe()),
                ("Perfil do Investidor", self.generate_profile_wireframe()),
                ("Resultados Detalhados", self.generate_detailed_results_wireframe())
            ]
            
            for title, fig in wireframes:
                pdf.savefig(fig, bbox_inches='tight', dpi=300)
                plt.close(fig)
                print(f"✅ Wireframe gerado: {title}")
        
        print(f"\n🎉 Todos os wireframes foram gerados com sucesso!")
        print(f"📄 Arquivo salvo: {filename}")

# Generate wireframes
if __name__ == "__main__":
    generator = WireframeGenerator()
    generator.generate_all_wireframes()