#!/bin/bash

# Script para download dos PDFs dos Wireframes
# Tenta múltiplos métodos para garantir sucesso

echo "🔄 Iniciando download dos PDFs dos Wireframes..."
echo "=========================================="

# Função para tentar download com diferentes métodos
download_file() {
    local filename=$1
    local url_localhost="http://localhost:8080/$filename"
    local url_ip="http://172.17.0.4:8080/$filename"
    
    echo "📥 Tentando baixar: $filename"
    
    # Método 1: wget com localhost
    echo "   Método 1: wget localhost..."
    if wget -q "$url_localhost" -O "$filename"; then
        echo "   ✅ Sucesso com wget localhost!"
        return 0
    fi
    
    # Método 2: curl com localhost
    echo "   Método 2: curl localhost..."
    if curl -s -o "$filename" "$url_localhost"; then
        echo "   ✅ Sucesso com curl localhost!"
        return 0
    fi
    
    # Método 3: wget com IP direto
    echo "   Método 3: wget IP direto..."
    if wget -q "$url_ip" -O "$filename"; then
        echo "   ✅ Sucesso com wget IP direto!"
        return 0
    fi
    
    # Método 4: curl com IP direto
    echo "   Método 4: curl IP direto..."
    if curl -s -o "$filename" "$url_ip"; then
        echo "   ✅ Sucesso com curl IP direto!"
        return 0
    fi
    
    # Método 5: wget com opções adicionais
    echo "   Método 5: wget com opções adicionais..."
    if wget --no-check-certificate --user-agent="Mozilla/5.0" -q "$url_localhost" -O "$filename"; then
        echo "   ✅ Sucesso com wget + opções!"
        return 0
    fi
    
    echo "   ❌ Falha em todos os métodos para $filename"
    return 1
}

# Verificar se o servidor está rodando
echo "🔍 Verificando servidor HTTP..."
if curl -s -I http://localhost:8080/ | grep -q "200 OK"; then
    echo "✅ Servidor HTTP está rodando"
else
    echo "❌ Servidor HTTP não está respondendo"
    echo "   Tentando acessar via IP..."
    if curl -s -I http://172.17.0.4:8080/ | grep -q "200 OK"; then
        echo "✅ Servidor acessível via IP 172.17.0.4"
    else
        echo "❌ Servidor não está acessível"
        exit 1
    fi
fi

echo ""
echo "🎯 Iniciando downloads..."
echo "========================="

# Lista de arquivos para download
files=(
    "wireframes_final.pdf"
    "wireframes_agente_investidor.pdf"
    "wireframes_agente_investidor_otimizado.pdf"
    "analise_fases_1_2.pdf"
)

# Contadores
success_count=0
total_files=${#files[@]}

# Fazer download de cada arquivo
for file in "${files[@]}"; do
    if download_file "$file"; then
        # Verificar se o arquivo foi baixado corretamente
        if [ -f "$file" ] && [ -s "$file" ]; then
            file_size=$(ls -lh "$file" | awk '{print $5}')
            echo "   📄 Arquivo salvo: $file ($file_size)"
            ((success_count++))
        else
            echo "   ❌ Arquivo vazio ou não foi salvo: $file"
        fi
    fi
    echo ""
done

echo "=========================================="
echo "🎉 RESUMO DO DOWNLOAD"
echo "=========================================="
echo "✅ Downloads bem-sucedidos: $success_count/$total_files"

if [ $success_count -eq $total_files ]; then
    echo "🎊 Todos os arquivos foram baixados com sucesso!"
    echo ""
    echo "📋 Arquivos disponíveis:"
    ls -lh *.pdf 2>/dev/null | grep -E "(wireframes|analise)" || echo "   Nenhum arquivo PDF encontrado"
else
    echo "⚠️  Alguns downloads falharam. Verifique:"
    echo "   - Se o servidor HTTP está rodando"
    echo "   - Se não há proxy/firewall bloqueando"
    echo "   - Se você tem permissões de escrita no diretório"
fi

echo ""
echo "🔧 Para troubleshooting, execute:"
echo "   curl -I http://localhost:8080/"
echo "   curl http://localhost:8080/"