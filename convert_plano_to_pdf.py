#!/usr/bin/env python3
"""
Script para converter os documentos do Plano de Ação para PDF
Autor: Claude Sonnet 4 - Análise Estratégica
Data: 15 de Janeiro de 2025
"""

import os
import sys
import subprocess
import markdown

def convert_markdown_to_html(md_file, html_file):
    """Converte arquivo Markdown para HTML"""
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Configurar extensões do markdown
        md = markdown.Markdown(extensions=[
            'tables',
            'fenced_code',
            'toc',
            'codehilite'
        ])
        
        # Converter para HTML
        html_content = md.convert(content)
        
        # Template HTML completo
        html_template = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plano de Ação - Agente Investidor</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #fff;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
        }}
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 5px;
            margin-top: 25px;
        }}
        h3 {{
            color: #2980b9;
            margin-top: 20px;
        }}
        h4 {{
            color: #27ae60;
            margin-top: 15px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: #fff;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        code {{
            background: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            border-left: 4px solid #3498db;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 20px 0;
            padding-left: 20px;
            font-style: italic;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
        }}
        .emoji {{
            font-size: 1.2em;
        }}
        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        li {{
            margin: 8px 0;
        }}
        .highlight {{
            background: #fff3cd;
            padding: 10px;
            border-left: 4px solid #ffc107;
            margin: 15px 0;
            border-radius: 3px;
        }}
        .success {{
            background: #d4edda;
            padding: 10px;
            border-left: 4px solid #28a745;
            margin: 15px 0;
            border-radius: 3px;
        }}
        .info {{
            background: #d1ecf1;
            padding: 10px;
            border-left: 4px solid #17a2b8;
            margin: 15px 0;
            border-radius: 3px;
        }}
        .warning {{
            background: #fff3cd;
            padding: 10px;
            border-left: 4px solid #ffc107;
            margin: 15px 0;
            border-radius: 3px;
        }}
        .danger {{
            background: #f8d7da;
            padding: 10px;
            border-left: 4px solid #dc3545;
            margin: 15px 0;
            border-radius: 3px;
        }}
        @media print {{
            body {{
                max-width: none;
                margin: 0;
                padding: 15px;
            }}
            h1 {{
                page-break-before: always;
            }}
            h1:first-child {{
                page-break-before: avoid;
            }}
            table {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
"""
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        print(f"✅ HTML gerado: {html_file}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar HTML: {e}")
        return False

def convert_html_to_pdf(html_file, pdf_file):
    """Converte arquivo HTML para PDF usando wkhtmltopdf"""
    try:
        # Comando para conversão
        cmd = [
            'wkhtmltopdf',
            '--page-size', 'A4',
            '--margin-top', '20mm',
            '--margin-right', '20mm',
            '--margin-bottom', '20mm',
            '--margin-left', '20mm',
            '--encoding', 'UTF-8',
            '--print-media-type',
            '--enable-local-file-access',
            html_file,
            pdf_file
        ]
        
        # Executar conversão
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ PDF gerado: {pdf_file}")
            return True
        else:
            print(f"❌ Erro na conversão: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ wkhtmltopdf não encontrado. Instalando...")
        try:
            # Tentar instalar wkhtmltopdf
            subprocess.run(['apt-get', 'update'], check=True)
            subprocess.run(['apt-get', 'install', '-y', 'wkhtmltopdf'], check=True)
            
            # Tentar novamente
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ PDF gerado: {pdf_file}")
                return True
            else:
                print(f"❌ Erro na conversão: {result.stderr}")
                return False
        except:
            print("❌ Não foi possível instalar wkhtmltopdf")
            return False
    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")
        return False

def alternative_pdf_conversion(md_file, pdf_file):
    """Conversão alternativa usando markdown e reportlab"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        
        # Ler conteúdo markdown
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Criar PDF
        doc = SimpleDocTemplate(pdf_file, pagesize=A4, topMargin=0.8*inch, bottomMargin=0.8*inch)
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2c3e50'),
            spaceBefore=20,
            spaceAfter=15
        )
        
        # Dividir conteúdo em seções
        lines = content.split('\n')
        for line in lines:
            if line.strip():
                if line.startswith('# '):
                    story.append(Paragraph(line[2:], title_style))
                elif line.startswith('## '):
                    story.append(Paragraph(line[3:], styles['Heading2']))
                elif line.startswith('### '):
                    story.append(Paragraph(line[4:], styles['Heading3']))
                else:
                    story.append(Paragraph(line, styles['Normal']))
                story.append(Spacer(1, 6))
        
        # Construir PDF
        doc.build(story)
        print(f"✅ PDF gerado (alternativo): {pdf_file}")
        return True
        
    except ImportError:
        print("❌ reportlab não instalado. Instalando...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'reportlab'], check=True)
            return alternative_pdf_conversion(md_file, pdf_file)
        except:
            print("❌ Não foi possível instalar reportlab")
            return False
    except Exception as e:
        print(f"❌ Erro na conversão alternativa: {e}")
        return False

def main():
    """Função principal"""
    
    # Arquivos para converter
    documents = [
        {
            'md': 'PLANO_ACAO_AGENTE_INVESTIDOR_2025.md',
            'pdf': 'PLANO_ACAO_AGENTE_INVESTIDOR_2025.pdf',
            'name': 'Plano de Ação Completo'
        },
        {
            'md': 'RESUMO_EXECUTIVO_AGENTE_INVESTIDOR.md',
            'pdf': 'RESUMO_EXECUTIVO_AGENTE_INVESTIDOR.pdf',
            'name': 'Resumo Executivo'
        }
    ]
    
    print("🔄 Iniciando conversão dos documentos para PDF...")
    print("=" * 60)
    
    # Instalar markdown se necessário
    try:
        import markdown
    except ImportError:
        print("📦 Instalando markdown...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'markdown'], check=True)
        import markdown
    
    success_count = 0
    
    for doc in documents:
        print(f"\n🔄 Convertendo: {doc['name']}")
        print(f"📄 Arquivo: {doc['md']}")
        
        if not os.path.exists(doc['md']):
            print(f"❌ Arquivo não encontrado: {doc['md']}")
            continue
        
        # Tentar conversão via HTML
        html_file = doc['md'].replace('.md', '.html')
        
        if convert_markdown_to_html(doc['md'], html_file):
            if convert_html_to_pdf(html_file, doc['pdf']):
                success_count += 1
                print(f"✅ {doc['name']} convertido com sucesso!")
            else:
                # Tentar conversão alternativa
                print("🔄 Tentando conversão alternativa...")
                if alternative_pdf_conversion(doc['md'], doc['pdf']):
                    success_count += 1
                    print(f"✅ {doc['name']} convertido com método alternativo!")
                else:
                    print(f"❌ Falha na conversão de {doc['name']}")
            
            # Limpar arquivo HTML temporário
            if os.path.exists(html_file):
                os.remove(html_file)
        else:
            print(f"❌ Erro ao processar {doc['name']}")
    
    print("\n" + "=" * 60)
    print(f"📊 Resultado: {success_count}/{len(documents)} documentos convertidos")
    
    if success_count > 0:
        print("\n✅ PDFs gerados com sucesso:")
        for doc in documents:
            if os.path.exists(doc['pdf']):
                size = os.path.getsize(doc['pdf']) / 1024
                print(f"  📄 {doc['pdf']} ({size:.1f} KB)")
    
    print("\n🎉 Conversão concluída!")

if __name__ == "__main__":
    main()