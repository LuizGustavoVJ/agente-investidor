#!/usr/bin/env python3
"""
Script para criar data URLs dos PDFs para download direto
"""

import os
import base64

def create_data_url_links():
    """Cria links data URL para download direto dos PDFs"""
    
    pdfs = [
        {
            'file': 'PLANO_ACAO_AGENTE_INVESTIDOR_2025.pdf',
            'name': 'Plano de Ação Completo - Agente Investidor 2025'
        },
        {
            'file': 'RESUMO_EXECUTIVO_AGENTE_INVESTIDOR.pdf',
            'name': 'Resumo Executivo - Agente Investidor 2025'
        }
    ]
    
    html_content = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Download Direto - PDFs Agente Investidor</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
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
            margin-bottom: 15px;
        }
        .download-btn {
            background: #3498db;
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            transition: background 0.3s;
            margin-right: 10px;
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
        .alert {
            background: #fff3cd;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 4px solid #ffc107;
        }
        .success {
            background: #d4edda;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 4px solid #28a745;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📄 Download Direto - PDFs Agente Investidor</h1>
        
        <div class="success">
            <h3>✅ Downloads Prontos!</h3>
            <p>Clique nos botões abaixo para download imediato dos PDFs.</p>
        </div>
    """
    
    for pdf in pdfs:
        if os.path.exists(pdf['file']):
            # Ler arquivo e converter para base64
            with open(pdf['file'], 'rb') as f:
                pdf_data = f.read()
            
            # Converter para base64
            base64_data = base64.b64encode(pdf_data).decode('utf-8')
            
            # Criar data URL
            data_url = f"data:application/pdf;base64,{base64_data}"
            
            # Calcular tamanho
            size = len(pdf_data) / 1024  # KB
            
            html_content += f"""
        <div class="pdf-item">
            <div class="pdf-title">{pdf['name']}</div>
            <a href="{data_url}" class="download-btn" download="{pdf['file']}">
                📥 Download {pdf['file']}
            </a>
            <div class="file-info">
                📄 Tamanho: {size:.1f} KB | 📅 Arquivo: {pdf['file']}
            </div>
        </div>
            """
    
    html_content += """
        <div class="instructions">
            <h3>📋 Como usar:</h3>
            <p><strong>1.</strong> Clique no botão "Download" do arquivo desejado</p>
            <p><strong>2.</strong> O arquivo será baixado automaticamente</p>
            <p><strong>3.</strong> Verifique a pasta de downloads do seu navegador</p>
        </div>
        
        <div class="alert">
            <h3>⚠️ Importante:</h3>
            <p>Se o download não funcionar automaticamente, clique com o botão direito no botão e selecione "Salvar link como..." ou "Save link as..."</p>
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

def main():
    """Função principal"""
    print("🔄 Criando links de download direto...")
    
    # Verificar se os PDFs existem
    pdfs = [
        'PLANO_ACAO_AGENTE_INVESTIDOR_2025.pdf',
        'RESUMO_EXECUTIVO_AGENTE_INVESTIDOR.pdf'
    ]
    
    missing_files = []
    for pdf in pdfs:
        if not os.path.exists(pdf):
            missing_files.append(pdf)
    
    if missing_files:
        print("❌ Arquivos não encontrados:")
        for file in missing_files:
            print(f"  - {file}")
        return
    
    # Criar página com data URLs
    html_content = create_data_url_links()
    
    with open('download_direct.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Página de download direto criada: download_direct.html")
    print("\n📋 INSTRUÇÕES:")
    print("1. Abra o arquivo 'download_direct.html' no seu navegador")
    print("2. Clique nos botões de download")
    print("3. Os PDFs serão baixados automaticamente")
    
    print("\n📄 Arquivos disponíveis:")
    for pdf in pdfs:
        if os.path.exists(pdf):
            size = os.path.getsize(pdf) / 1024
            print(f"  ✅ {pdf} ({size:.1f} KB)")
    
    print("\n🎉 Tudo pronto! Abra o arquivo 'download_direct.html' para baixar os PDFs.")

if __name__ == "__main__":
    main()