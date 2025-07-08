# Documentação Técnica das Funções Backend

## main.py
- Inicializa o app Flask, configura CORS, banco, blueprints e rotas principais.
- Fallback SPA: serve index.html para qualquer rota desconhecida.

## Blueprints
### routes/user.py
- `/api/auth/login` (POST): Login, retorna JWT.
- `/api/auth/register` (POST): Cadastro de usuário.
- `/api/auth/validate` (GET): Valida JWT.
- Funções auxiliares: geração e validação de JWT, autenticação.

### routes/agente.py
- `/api/dados-mercado` (GET): Dados de mercado (Ibovespa, dólar, etc).
- `/api/dados-acao/<symbol>` (GET): Dados de uma ação específica.
- `/api/analisar-acao` (POST): Recebe dados e retorna análise fundamentalista.
- `/api/chat` (POST): Chat com agente investidor.
- Funções de análise, integração com dados externos, lógica de recomendação.

## Models
### models/user.py
- Classe User: id, username, email, senha (hash), métodos de autenticação.
### models/investidor.py
- Classe Investidor: perfil, preferências, métodos de análise.
### models/acao.py
- Classe Acao: dados de ações, métodos de consulta.
### models/analise_financeira.py
- Classe AnaliseFinanceira: lógica de análise, cálculo de scores, recomendações.

## Exemplos de Uso das APIs
### Login
```http
POST /api/auth/login
{
  "username": "user",
  "password": "senha"
}
```
Resposta:
```json
{
  "access_token": "<jwt>"
}
```

### Análise de Ação
```http
POST /api/analisar-acao
Authorization: Bearer <jwt>
{
  "symbol": "PETR4.SA",
  "metodologia": "warren_buffett"
}
```
Resposta:
```json
{
  "success": true,
  "data": {
    "score": 87,
    "recomendacao": "Comprar",
    ...
  }
}
```

## Observações
- Todas as rotas protegidas exigem JWT no header Authorization.
- Funções utilitárias para manipulação de tokens, hashing de senha, validação de dados e integração com fontes externas estão documentadas nos próprios arquivos Python via docstrings. 