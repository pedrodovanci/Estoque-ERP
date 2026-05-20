# Estoque-ERP — Módulo de Estoque (API FastAPI + Supabase)

Este repositório contém o **módulo de Estoque** de um ERP universitário. Ele é um **serviço independente** com **banco próprio** (Supabase/PostgreSQL) e expõe uma **API FastAPI** para o **Core** (e outros módulos) consumirem via HTTP.

```
[Core (server-to-server)] ───────────────► [Estoque API :8003]
                                              │
                                              ▼
                                      [Supabase PostgreSQL]
```

## Estrutura atual do projeto

```
Estoque-ERP/
├── README.md
├── README_banco.md
├── .gitignore
├── requirements.txt
└── modulo-estoque/
    ├── .env.example
    ├── requirements.txt
    ├── app/
    │   ├── main.py
    │   ├── core/
    │   │   ├── config.py
    │   │   ├── database.py
    │   │   └── security.py
    │   ├── models/
    │   │   ├── produto.py
    │   │   └── movimentacao.py
    │   ├── schemas/
    │   │   ├── produto.py
    │   │   └── movimentacao.py
    │   ├── services/
    │   │   └── estoque_service.py
    │   └── routers/
    │       ├── produtos.py
    │       ├── movimentacoes.py
    │       └── alertas.py
    └── tests/
        ├── conftest.py
        ├── test_produtos.py
        ├── test_movimentacoes.py
        └── test_alertas_inventario.py
```

## Stack

- **FastAPI** + **Uvicorn**
- **SQLAlchemy** + **psycopg2-binary**
- **Pydantic v2** (aliases para `camelCase`)
- **pytest** (testes automatizados)
- **Supabase** (PostgreSQL gerenciado)

## Banco de dados (Supabase)

O banco é descrito em detalhes em [README_banco.md](./README_banco.md).

- Tabelas principais:
  - `produtos`
  - `movimentacoes_estoque`
- View (se você executar o `views.sql` do banco):
  - `vw_alertas_estoque`

Regras importantes do contrato do banco:
- `sku` é único.
- `saldo_atual` nunca pode ficar negativo.
- Tipos de movimentação: `entrada`, `saida`, `inventario`.

## Variáveis de ambiente

Crie `modulo-estoque/.env` (não versionar).

Mínimo para rodar:

```env
DATABASE_URL=postgresql://postgres:SUA_SENHA@db.SEUID.supabase.co:5432/postgres?sslmode=require
FRONTEND_URL=http://localhost:3000
```

Autenticação (recomendado em produção):

```env
AUTH_ENABLED=true
CORE_JWT_SECRET=SEGREDO_DO_CORE
CORE_JWT_ALG=HS256
CORE_JWT_ISSUER=core
```

Observação sobre `DATABASE_URL`:
- Se sua senha tiver `@`, precisa fazer URL-encoding (`@` → `%40`).
- O módulo também faz uma normalização automática para esse caso e adiciona `sslmode=require` quando detectar Supabase.

## Autenticação (Core → Estoque)

O Core **emite** o token e o módulo **apenas valida**. A validação só é aplicada quando `AUTH_ENABLED=true`.

Headers aceitos:
- Preferencial: `Authorization: Bearer <jwt>`
- Alternativo: `X-Service-Token: <jwt>`

Validações aplicadas:
- assinatura do JWT (`CORE_JWT_SECRET` e `CORE_JWT_ALG`)
- claim `iss` (se `CORE_JWT_ISSUER` estiver definido)

## Como rodar localmente

### 1) Instalar dependências

```bash
cd modulo-estoque
pip install -r requirements.txt
```

### 2) Subir a API

Porta padrão do módulo: `8003`

```bash
py -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

Para testar pelo Swagger na porta `8000`:

```bash
py -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Acessos:
- Swagger: `http://localhost:8003/docs` (ou `:8000/docs`)
- OpenAPI JSON: `http://localhost:8003/openapi.json`
- Health: `http://localhost:8003/health`

Se você rodar o comando a partir da raiz do repositório, use:

```bash
py -m uvicorn app.main:app --app-dir modulo-estoque --host 0.0.0.0 --port 8003 --reload
```

## Endpoints

Todas as rotas do módulo ficam em `/estoque/*`.

### Health

- `GET /health`

### Produtos (CRUD + consulta de saldo)

- `GET /estoque/produtos?page=1&size=10&sku=CAM-001`
- `GET /estoque/produtos/{id}`
- `POST /estoque/produtos`
- `PUT /estoque/produtos/{id}`
- `DELETE /estoque/produtos/{id}`
  - retorna `409` se houver movimentações registradas para o produto

Exemplo de criação:

```json
{
  "nome": "Camiseta ERP Universitario",
  "sku": "CAM-001",
  "unidade": "un",
  "saldoAtual": 50,
  "estoqueMinimo": 10
}
```

### Movimentações de estoque

- `POST /estoque/movimentacoes/entrada`
- `POST /estoque/movimentacoes/saida`
- `GET /estoque/movimentacoes/{prod_id}` (histórico)

Entrada:

```json
{ "produtoId": 1, "quantidade": 5 }
```

Saída:

```json
{ "produtoId": 1, "quantidade": 2 }
```

### Alertas e inventário

- `GET /estoque/alertas`
- `POST /estoque/inventario/{prod_id}`

Inventário:

```json
{
  "saldoAjustado": 7,
  "justificativa": "contagem física"
}
```

## Mapeamento snake_case ↔ camelCase

O banco usa `snake_case`. A API responde em `camelCase` nos campos que o frontend/core precisam:

- `saldo_atual` → `saldoAtual`
- `estoque_minimo` → `estoqueMinimo`
- `produto_id` → `produtoId`
- `saldo_ajustado` → `saldoAjustado`

## Regras de negócio implementadas

- Entrada soma no saldo (`saldo_atual`).
- Saída diminui do saldo e **não permite saldo negativo** (retorna 422).
- Inventário ajusta o saldo para o valor informado e registra justificativa.
- Toda operação registra histórico em `movimentacoes_estoque`.

## Testes

Os testes sobem um SQLite em memória e validam os fluxos principais.

```bash
cd modulo-estoque
pytest -q
```

## Troubleshooting

- `ModuleNotFoundError: No module named 'app'`
  - Você está rodando o Uvicorn na pasta errada. Rode dentro de `modulo-estoque/` ou use `--app-dir modulo-estoque`.
- Erro 500 em qualquer rota que acessa o banco
  - Verifique `DATABASE_URL` (especialmente senha com `@`) e se o Supabase está acessível.
  - Para Supabase, garanta `?sslmode=require`.
