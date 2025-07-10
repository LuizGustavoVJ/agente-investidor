# Agente Investidor

## Visão Geral
Sistema web para análise de ações, dashboard de mercado, chat inteligente e metodologias de investimento, inspirado em grandes investidores como Warren Buffett, Graham, Lynch e Barsi. Backend em Flask (MVC), frontend SPA com HTML/CSS/JS puro.

## Arquitetura
- **Backend:** Flask, padrão MVC, autenticação JWT, rotas RESTful.
- **Frontend:** SPA (Single Page Application) com navegação dinâmica via JS.
- **Banco de Dados:** SQLite (SQLAlchemy ORM).
- **APIs:** Dados de mercado, análise de ações, chat, autenticação.

## Instalação
1. Clone o repositório:
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

## Estrutura de Pastas
```
├── src/
│   ├── main.py           # App Flask principal
│   ├── models/           # Modelos ORM (User, Investidor, Ação, Análise)
│   ├── routes/           # Blueprints de rotas (user, agente)
│   ├── views/            # Templates HTML (index, login, cadastro)
│   ├── static/           # JS, CSS, imagens
│   ├── database/         # Banco SQLite
│   └── data.py           # Lógica de dados/mercado
├── requirements.txt      # Dependências Python
├── README.md             # Documentação principal
└── test_apis.py          # Testes de API
```

## Autenticação JWT
- Login gera um JWT salvo no localStorage do navegador.
- Rotas protegidas exigem envio do token no header Authorization.
- Claims customizados podem ser adicionados ao token (ex: roles, expiração).

## Navegação SPA
- Todas as seções (Home, Dashboard, Análise, Chat, Metodologias) estão em `views/index.html`.
- Navegação via JS (`showSection`) sem recarregar a página.
- Botões do menu ativam/desativam seções dinamicamente.

## Principais Arquivos
- `src/main.py`: inicialização Flask, rotas principais, fallback SPA.
- `src/routes/user.py`: autenticação, cadastro, login, geração/validação JWT.
- `src/routes/agente.py`: APIs de análise, chat, dados de mercado.
- `src/models/`: entidades do sistema (usuário, investidor, ação, análise).
- `src/views/index.html`: SPA principal, navegação e seções.
- `src/static/script.js`: lógica SPA, integração API, gráficos, chat.
- `src/static/styles.css`: estilos visuais responsivos.

## Fluxo de Autenticação
1. Usuário acessa `/login` → envia credenciais.
2. Backend valida e retorna JWT.
3. Frontend salva JWT no localStorage.
4. Navegação SPA exibe menu do usuário logado.
5. Logout remove JWT e redireciona para login.

## Desenvolvimento
- Siga o padrão MVC: views em `views/`, lógica em `routes/`, modelos em `models/`.
- Use `render_template` para servir HTML.
- JS deve exportar funções globais usadas em `onclick`.
- Testes de API em `test_apis.py`.

## Contato
Desenvolvido por Luiz Gustavo Finotello. 