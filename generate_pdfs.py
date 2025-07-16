#!/usr/bin/env python3
"""
Script simplificado para converter os documentos do Plano de Ação para PDF
Usando weasyprint para gerar PDFs de alta qualidade
"""

import os
import sys
import markdown
import weasyprint

def create_html_template(content, title):
    """Cria template HTML estilizado"""
    return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
            @bottom-right {{
                content: counter(page);
                font-size: 10px;
                color: #666;
            }}
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            font-size: 12px;
            margin: 0;
            padding: 0;
        }}
        
        h1 {{
            color: #2c3e50;
            font-size: 24px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
            margin-bottom: 20px;
            page-break-before: auto;
        }}
        
        h2 {{
            color: #34495e;
            font-size: 20px;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 5px;
            margin-top: 25px;
            margin-bottom: 15px;
        }}
        
        h3 {{
            color: #2980b9;
            font-size: 16px;
            margin-top: 20px;
            margin-bottom: 12px;
        }}
        
        h4 {{
            color: #27ae60;
            font-size: 14px;
            margin-top: 15px;
            margin-bottom: 10px;
        }}
        
        p {{
            margin-bottom: 12px;
            text-align: justify;
        }}
        
        ul, ol {{
            margin: 12px 0;
            padding-left: 25px;
        }}
        
        li {{
            margin: 6px 0;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 11px;
            page-break-inside: avoid;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        
        code {{
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 11px;
        }}
        
        pre {{
            background-color: #f8f9fa;
            padding: 12px;
            border-radius: 5px;
            overflow-x: auto;
            border-left: 4px solid #3498db;
            font-size: 10px;
            margin: 15px 0;
        }}
        
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 15px 0;
            padding: 10px 15px;
            background-color: #f8f9fa;
            font-style: italic;
        }}
        
        .highlight {{
            background-color: #fff3cd;
            padding: 8px;
            border-left: 4px solid #ffc107;
            margin: 10px 0;
        }}
        
        .page-break {{
            page-break-before: always;
        }}
        
        .no-break {{
            page-break-inside: avoid;
        }}
        
        hr {{
            border: none;
            height: 2px;
            background-color: #ecf0f1;
            margin: 20px 0;
        }}
        
        strong {{
            color: #2c3e50;
        }}
        
        em {{
            color: #7f8c8d;
        }}
        
        .emoji {{
            font-size: 1.2em;
        }}
    </style>
</head>
<body>
    {content}
</body>
</html>
"""

def convert_markdown_to_pdf(md_file, pdf_file, title):
    """Converte arquivo markdown para PDF"""
    try:
        print(f"🔄 Convertendo {md_file} para {pdf_file}...")
        
        # Ler arquivo markdown
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Converter markdown para HTML
        md = markdown.Markdown(extensions=[
            'tables',
            'fenced_code',
            'codehilite',
            'toc'
        ])
        html_content = md.convert(md_content)
        
        # Criar HTML completo
        html = create_html_template(html_content, title)
        
        # Converter HTML para PDF
        weasyprint.HTML(string=html).write_pdf(pdf_file)
        
        # Verificar se o arquivo foi criado
        if os.path.exists(pdf_file):
            size = os.path.getsize(pdf_file) / 1024  # KB
            print(f"✅ PDF criado: {pdf_file} ({size:.1f} KB)")
            return True
        else:
            print(f"❌ Erro: PDF não foi criado")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao converter {md_file}: {str(e)}")
        return False

def main():
    """Função principal"""
    
    # Documentos para converter
    documents = [
        {
            'md': 'PLANO_ACAO_AGENTE_INVESTIDOR_2025.md',
            'pdf': 'PLANO_ACAO_AGENTE_INVESTIDOR_2025.pdf',
            'title': 'Plano de Ação Estratégico - Agente Investidor 2025'
        },
        {
            'md': 'RESUMO_EXECUTIVO_AGENTE_INVESTIDOR.md',
            'pdf': 'RESUMO_EXECUTIVO_AGENTE_INVESTIDOR.pdf',
            'title': 'Resumo Executivo - Agente Investidor 2025'
        }
    ]
    
    print("🚀 Gerando PDFs do Plano de Ação - Agente Investidor")
    print("=" * 60)
    
    success_count = 0
    
    for doc in documents:
        if not os.path.exists(doc['md']):
            print(f"❌ Arquivo não encontrado: {doc['md']}")
            continue
            
        if convert_markdown_to_pdf(doc['md'], doc['pdf'], doc['title']):
            success_count += 1
        
        print()  # Linha em branco
    
    print("=" * 60)
    print(f"📊 Resultado: {success_count}/{len(documents)} documentos convertidos com sucesso")
    
    if success_count > 0:
        print("\n✅ PDFs disponíveis para download:")
        for doc in documents:
            if os.path.exists(doc['pdf']):
                size = os.path.getsize(doc['pdf']) / 1024
                print(f"  📄 {doc['pdf']} ({size:.1f} KB)")
    
    print("\n🎉 Processamento concluído!")

if __name__ == "__main__":
    main()