#!/usr/bin/env python3
"""
Script para converter Wireframes Markdown para PDF
Autor: Luiz Gustavo Finotello
Data: 16 de Janeiro de 2025
"""

import markdown_pdf
import sys
import os

def convert_with_markdown_pdf(input_md, output_pdf):
    """Converte arquivo Markdown para PDF usando markdown_pdf"""
    
    try:
        # Ler conteúdo do arquivo
        with open(input_md, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Criar PDF
        pdf = markdown_pdf.MarkdownPdf()
        
        # Criar seção com o conteúdo do arquivo
        section = markdown_pdf.Section(content)
        pdf.add_section(section)
        
        pdf.save(output_pdf)
        print(f"✅ PDF gerado com sucesso: {output_pdf}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")
        return False

def main():
    input_md = "wireframes_final.md"
    output_pdf = "wireframes_final.pdf"
    
    if not os.path.exists(input_md):
        print(f"❌ Arquivo não encontrado: {input_md}")
        sys.exit(1)
    
    print(f"🔄 Convertendo {input_md} para {output_pdf}...")
    
    success = convert_with_markdown_pdf(input_md, output_pdf)
    
    if success:
        print(f"📄 PDF salvo em: {os.path.abspath(output_pdf)}")
        if os.path.exists(output_pdf):
            print(f"📊 Tamanho do arquivo: {os.path.getsize(output_pdf) / 1024:.1f} KB")
    else:
        print("❌ Falha na conversão")

if __name__ == "__main__":
    main()