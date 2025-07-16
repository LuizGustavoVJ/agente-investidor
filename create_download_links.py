#!/usr/bin/env python3
"""
Script para criar links de download dos PDFs
"""

import os
import base64
import webbrowser
from urllib.parse import quote

def create_download_html():
    """Cria uma página HTML com links de download"""
    
    pdfs = [
        {
            'file': 'PLANO_ACAO_AGENTE_INVESTIDOR_2025.pdf',
            'name': 'Plano de Ação Completo - Agente Investidor 2025',
            'description': 'Documento estratégico completo com análise competitiva, plano de implementação, especificações técnicas e roadmap detalhado.'
        },
        {
            'file': 'RESUMO_EXECUTIVO_AGENTE_INVESTIDOR.pdf', 
            'name': 'Resumo Executivo - Agente Investidor 2025',
            'description': 'Resumo executivo conciso para apresentação aos stakeholders com análise competitiva e estratégia de implementação.'
        }
    ]
    
    html_content = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Download - Plano de Ação Agente Investidor</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
        }
        .pdf-item {
            background: #f8f9fa;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }
        .pdf-title {
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 8px;
        }
        .pdf-description {
            color: #666;
            margin-bottom: 15px;
            line-height: 1.5;
        }
        .download-btn {
            background: #3498db;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            font-size: 14px;
            transition: background 0.3s;
        }
        .download-btn:hover {
            background: #2980b9;
        }
        .file-info {
            color: #7f8c8d;
            font-size: 12px;
            margin-top: 10px;
        }
        .instructions {
            background: #e8f5e8;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 4px solid #27ae60;
        }
        .server-info {
            background: #fff3cd;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 4px solid #ffc107;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📄 Download - Plano de Ação Agente Investidor 2025</h1>
        
        <div class="instructions">
            <h3>📋 Instruções para Download:</h3>
            <p><strong>Método 1:</strong> Clique nos botões de download abaixo</p>
            <p><strong>Método 2:</strong> Acesse os links diretos no servidor HTTP</p>
            <p><strong>Método 3:</strong> Use o navegador para acessar os arquivos</p>
        </div>
        
        <div class="server-info">
            <h3>🌐 Servidor HTTP Ativo:</h3>
            <p><strong>URL:</strong> <code>http://localhost:8080</code></p>
            <p><strong>Status:</strong> Servidor rodando em background</p>
            <p>Navegue até a URL acima para ver todos os arquivos disponíveis</p>
        </div>
    """
    
    for pdf in pdfs:
        if os.path.exists(pdf['file']):
            size = os.path.getsize(pdf['file']) / 1024  # KB
            html_content += f"""
        <div class="pdf-item">
            <div class="pdf-title">{pdf['name']}</div>
            <div class="pdf-description">{pdf['description']}</div>
            <a href="{pdf['file']}" class="download-btn" download="{pdf['file']}">
                📥 Download {pdf['file']}
            </a>
            <div class="file-info">
                📄 Tamanho: {size:.1f} KB | 📅 Gerado: {os.path.getmtime(pdf['file'])}
            </div>
        </div>
            """
    
    html_content += """
        <div class="instructions">
            <h3>🔧 Alternativas de Download:</h3>
            <p><strong>1.</strong> Servidor HTTP: <a href="http://localhost:8080" target="_blank">http://localhost:8080</a></p>
            <p><strong>2.</strong> Copiar arquivos manualmente do workspace</p>
            <p><strong>3.</strong> Usar comando wget/curl se disponível</p>
        </div>
        
        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 2px solid #ecf0f1;">
            <p><strong>🚀 Pronto para transformar o Agente Investidor na referência do mercado!</strong></p>
            <p style="color: #666; font-size: 12px;">Documento gerado por Claude Sonnet 4 - Análise Estratégica</p>
        </div>
    </div>
</body>
</html>
    """
    
    return html_content

def create_download_page():
    """Cria página HTML de download"""
    html_content = create_download_html()
    
    with open('download_pdfs.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Página de download criada: download_pdfs.html")
    return True

def show_download_options():
    """Mostra opções de download"""
    print("🚀 OPÇÕES DE DOWNLOAD DOS PDFs")
    print("=" * 50)
    
    # Verificar arquivos
    pdfs = [
        'PLANO_ACAO_AGENTE_INVESTIDOR_2025.pdf',
        'RESUMO_EXECUTIVO_AGENTE_INVESTIDOR.pdf'
    ]
    
    print("\n📄 Arquivos disponíveis:")
    for pdf in pdfs:
        if os.path.exists(pdf):
            size = os.path.getsize(pdf) / 1024
            print(f"  ✅ {pdf} ({size:.1f} KB)")
        else:
            print(f"  ❌ {pdf} (não encontrado)")
    
    print("\n🌐 MÉTODO 1 - Servidor HTTP (RECOMENDADO):")
    print("  1. Abra seu navegador")
    print("  2. Acesse: http://localhost:8080")
    print("  3. Clique nos arquivos PDF para baixar")
    
    print("\n📋 MÉTODO 2 - Página de Download:")
    print("  1. Abra o arquivo: download_pdfs.html")
    print("  2. Clique nos botões de download")
    
    print("\n💻 MÉTODO 3 - Linha de Comando:")
    print("  # Para baixar via wget (se disponível):")
    for pdf in pdfs:
        if os.path.exists(pdf):
            print(f"  wget http://localhost:8080/{pdf}")
    
    print("\n📁 MÉTODO 4 - Copiar Arquivos:")
    print("  Os arquivos estão em: /workspace/")
    for pdf in pdfs:
        if os.path.exists(pdf):
            print(f"  - {os.path.abspath(pdf)}")

if __name__ == "__main__":
    print("🔄 Preparando opções de download...")
    
    # Criar página de download
    create_download_page()
    
    # Mostrar opções
    show_download_options()
    
    print("\n🎉 Tudo pronto! Use qualquer um dos métodos acima para baixar os PDFs.")