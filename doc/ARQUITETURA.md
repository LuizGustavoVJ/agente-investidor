# Arquitetura do Agente Investidor

## Visão Geral
O sistema segue o padrão MVC no backend (Flask) e SPA no frontend (HTML/JS). A comunicação entre frontend e backend é feita via APIs REST protegidas por JWT.

## Diagrama de Componentes
```
Usuário
  │
  ▼
Frontend (index.html, script.js)
  │  (fetch, localStorage JWT)
  ▼
Backend Flask (main.py, routes/)
  │  (validação JWT, lógica de negócio)
  ▼
Modelos ORM (models/)
  │
  ▼
Banco SQLite
```

## Fluxo de Autenticação JWT
1. Usuário faz login via `/login`.
2. Backend valida e retorna JWT.
3. Frontend salva JWT no localStorage.
4. Para cada requisição protegida, frontend envia JWT no header Authorization.
5. Backend valida JWT antes de responder.

## Navegação SPA
- Todas as seções estão em um único HTML (`index.html`).
- Navegação é feita via JS, exibindo/escondendo seções.
- Não há reload de página, apenas manipulação do DOM.

## Organização dos Módulos
- `main.py`: inicialização Flask, fallback SPA, registro de blueprints.
- `routes/`: APIs de autenticação, análise, chat, dados de mercado.
- `models/`: entidades ORM (usuário, investidor, ação, análise).
- `views/`: HTMLs (SPA, login, cadastro).
- `static/`: JS, CSS, imagens.

## Integração Backend/Frontend
- Frontend consome APIs REST do backend.
- JWT é usado para autenticação e autorização.
- Dados dinâmicos (dashboard, análise, chat) são carregados via fetch. 