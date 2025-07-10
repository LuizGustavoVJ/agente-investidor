# Guia de Uso do Agente Investidor

## Instalação e Execução
1. Clone o repositório e entre na pasta:
   ```bash
   git clone <repo-url>
   cd agente-investidor-main
   ```
2. Crie e ative o ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate    # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Execute o servidor:
   ```bash
   python src/main.py
   ```
5. Acesse `http://localhost:5000` no navegador.

## Cadastro e Login
- Acesse `/cadastro` para criar uma conta.
- Após cadastro, faça login em `/login`.
- O JWT será salvo automaticamente e o menu do usuário aparecerá.

## Navegação SPA
- Use o menu superior para alternar entre Home, Dashboard, Análise, Chat e Metodologias.
- As seções são exibidas dinamicamente sem recarregar a página.

## Análise de Ações
- Vá para "Análise".
- Selecione uma ação e metodologia.
- Clique em "Analisar Ação" para ver resultados, gráficos e recomendações.

## Dashboard
- Acesse "Dashboard" para ver indicadores de mercado, gráficos e destaques.

## Chat Inteligente
- Acesse "Chat" para conversar com o agente investidor.
- Use sugestões rápidas ou digite perguntas sobre investimentos.

## Logout
- Clique no nome do usuário no menu e selecione "Logout" para sair. 