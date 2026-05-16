# Guia de Implementação — Módulo Estoque (G4)

### FastAPI + Supabase | Passo a passo do zero

---

## Visão geral do que você vai construir

```
[Frontend :3000] ──────────────────────────────────► [Seu backend :8003]
                                                            │
[Compras  :8004] ──► POST /estoque/movimentacoes/entrada    │
                                                            ▼
                                              [Supabase PostgreSQL]
```

Seu backend é uma API FastAPI que roda na nuvem. O Supabase fornece o banco PostgreSQL — você não precisa instalar nem gerenciar nenhum banco localmente.

---

## Pré-requisitos

- Python 3.11+ instalado
- Conta no [Supabase](https://supabase.com) (gratuita)
- Conta no [Railway](https://railway.app) ou [Render](https://render.com) para deploy (gratuitos)
- Git instalado

---

## Checklist de execução (micro-tasks)

### Passo 1 — Supabase

- [ ] Criar conta no Supabase
- [ ] Criar projeto (**New Project**) com nome `erp-estoque`
- [ ] Definir região (South America) e senha forte
- [ ] Copiar a **Connection String** em **Settings → Database**
- [ ] Ajustar a string adicionando `?sslmode=require` no final
- [ ] Copiar e guardar **URL** e **anon key** em **Settings → API**

### Passo 2 — Estrutura do projeto

- [ ] Criar pasta `modulo-estoque/`
- [ ] Criar a estrutura `app/` (core, models, schemas, routers, services)
- [ ] Criar `tests/`
- [ ] Criar arquivos `__init__.py` e `app/main.py`

### Passo 3 — Ambiente e dependências

- [ ] Criar `venv` (Python)
- [ ] Ativar `venv`
- [ ] Instalar dependências (FastAPI, Uvicorn, SQLAlchemy, Alembic, etc.)
- [ ] Gerar `requirements.txt`

### Passo 4 — Variáveis e Git

- [ ] Criar `.env` na raiz (com `DATABASE_URL`, `CORE_URL`, `SECRET_KEY`, `FRONTEND_URL`)
- [ ] Criar `.env.example` (sem valores reais)
- [ ] Criar `.gitignore` (garantir que `.env` e `venv/` não sobem)

### Passo 5 — Config e banco

- [ ] Criar `app/core/config.py` e carregar `.env`
- [ ] Instalar `pydantic-settings` e atualizar `requirements.txt`
- [ ] Criar `app/core/database.py` com `engine`, `SessionLocal`, `Base` e `get_db()`

### Passo 6 — Models

- [ ] Criar `app/models/produto.py` (tabela `produtos`)
- [ ] Criar `app/models/movimentacao.py` (tabela `movimentacoes` + enum de tipo)
- [ ] Confirmar campos mínimos: SKU/código, descrição, unidade, quantidade, estoque_minimo, custo, ativo

### Passo 7 — Schemas

- [ ] Criar `app/schemas/produto.py` (Create/Update/Response)
- [ ] Criar `app/schemas/movimentacao.py` (Entrada/Saída/Ajuste + Response)

### Passo 8 — Regras de negócio (Service)

- [ ] Implementar `registrar_entrada()` (incrementa estoque + grava movimentação)
- [ ] Implementar `registrar_saida()` (valida estoque não-negativo + grava movimentação)
- [ ] Validar retornos e erros (404 produto não encontrado, 422 saldo insuficiente)

### Passo 9 — Endpoints (Routers)

- [ ] Criar router `produtos` (listar/cadastrar/detalhar/atualizar)
- [ ] Criar router `alertas` (listar produtos abaixo do mínimo)
- [ ] Criar router `movimentacoes` (entrada/saida/histórico)
- [ ] Marcar pendência: substituir `usuario_id=1` por ID vindo do JWT

### Passo 10 — Aplicação (Main)

- [ ] Criar `app/main.py` com FastAPI + CORS
- [ ] Incluir routers de produtos/movimentações/alertas
- [ ] Subir aplicação criando tabelas no Supabase (primeira execução)

### Passo 11 — Rodar localmente

- [ ] Subir com `uvicorn` na porta `8003`
- [ ] Validar `/health`
- [ ] Abrir Swagger em `/docs`
- [ ] Confirmar tabelas no Supabase (**Table Editor**)

### Passo 12 — Migrations (Alembic)

- [ ] `alembic init alembic`
- [ ] Configurar `target_metadata` no `alembic/env.py`
- [ ] Configurar `sqlalchemy.url = %(DATABASE_URL)s` no `alembic.ini`
- [ ] Adicionar `load_dotenv()` no `alembic/env.py`
- [ ] Gerar migration inicial (`revision --autogenerate`)
- [ ] Aplicar migration (`upgrade head`)

### Passo 13 — Deploy

- [ ] Fazer push para GitHub (sem `.env`)
- [ ] Conectar repositório no Railway/Render
- [ ] Criar variáveis de ambiente no painel
- [ ] Configurar comando de start (uvicorn com `$PORT`)
- [ ] Validar URL pública e compartilhar com Frontend/Core

### Próximos passos (depois do básico rodar)

- [ ] Validar JWT nos endpoints (integração com o Core)
- [ ] Criar seed (dados de exemplo)
- [ ] Escrever testes com pytest (meta ≥ 70% de cobertura)
- [ ] Implementar inventário (`/estoque/inventario/{prod_id}`)
- [ ] Melhorar paginação e filtros
- [ ] Docker Compose (bônus)

---

## Passo 1 — Criar o projeto no Supabase

1. Acesse [supabase.com](https://supabase.com) e crie uma conta
2. Clique em **New Project**
3. Dê o nome `erp-estoque`, escolha uma senha forte e selecione a região mais próxima (South America)
4. Aguarde o projeto ser criado (~2 minutos)
5. Vá em **Settings → Database** e copie a **Connection String** no formato:
   ```
   postgresql://postgres:[SUA_SENHA]@db.[SEU_ID].supabase.co:5432/postgres
   ```
6. Guarde também a **URL** e a **anon key** em **Settings → API** (vão ser usadas depois)

> **Importante:** Use a connection string com `?sslmode=require` no final para funcionar corretamente.
>
> **Atenção ao `@`:** na URL de conexão, o `@` separa as credenciais do host (`usuario:senha@host`). Ele não faz parte da senha.
>
> **Senha com caracteres especiais:** se a senha tiver caracteres como `{` ou `}`, faça URL-encoding (ex: `{` → `%7B`, `}` → `%7D`) para evitar erro de parsing.

---

## Passo 2 — Estrutura do projeto

No seu computador, crie a seguinte estrutura de pastas:

```
modulo-estoque/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # variáveis de ambiente
│   │   ├── database.py      # conexão com Supabase via SQLAlchemy
│   │   └── security.py      # validação do JWT com o Core
│   ├── models/
│   │   ├── __init__.py
│   │   ├── produto.py       # tabela produtos
│   │   └── movimentacao.py  # tabela movimentacoes
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── produto.py       # formatos de entrada e saída da API
│   │   └── movimentacao.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── produtos.py      # endpoints /estoque/produtos
│   │   ├── movimentacoes.py # endpoints /estoque/movimentacoes
│   │   ├── alertas.py       # endpoint /estoque/alertas
│   │   └── inventario.py    # endpoint /estoque/inventario
│   ├── services/
│   │   ├── __init__.py
│   │   └── estoque_service.py  # regras de negócio (ex: estoque nunca negativo)
│   └── main.py              # ponto de entrada da aplicação
├── tests/
│   ├── __init__.py
│   ├── test_produtos.py
│   └── test_movimentacoes.py
├── .env                     # variáveis locais (nunca suba para o GitHub)
├── .env.example             # modelo sem valores reais (suba para o GitHub)
├── .gitignore
├── requirements.txt
└── README.md
```

Para criar as pastas de uma vez, rode no terminal:

```bash
mkdir -p modulo-estoque/app/{core,models,schemas,routers,services}
mkdir -p modulo-estoque/tests
cd modulo-estoque
touch app/__init__.py app/core/__init__.py app/models/__init__.py
touch app/schemas/__init__.py app/routers/__init__.py app/services/__init__.py
touch app/main.py tests/__init__.py
```

---

## Passo 3 — Ambiente virtual e dependências

```bash
# dentro da pasta modulo-estoque/
python -m venv venv

# ativar no Windows
venv\Scripts\activate

# ativar no Mac/Linux
source venv/bin/activate

# instalar as dependências
pip install fastapi uvicorn sqlalchemy alembic psycopg2-binary \
            python-dotenv python-jose[cryptography] httpx pytest pytest-cov
```

Gere o `requirements.txt`:

```bash
pip freeze > requirements.txt
```

---

## Passo 4 — Variáveis de ambiente

Crie o arquivo `.env` na raiz do projeto:

```env
DATABASE_URL=postgresql+psycopg2://postgres:[SUA_SENHA]@db.[SEU_ID].supabase.co:5432/postgres?sslmode=require
CORE_URL=http://localhost:8000
SECRET_KEY=uma_chave_secreta_qualquer_para_desenvolvimento
FRONTEND_URL=http://localhost:3000
```

Crie o `.env.example` (sem valores reais, para o GitHub):

```env
DATABASE_URL=postgresql+psycopg2://postgres:SENHA@db.ID.supabase.co:5432/postgres?sslmode=require
CORE_URL=http://localhost:8000
SECRET_KEY=sua_chave_secreta
FRONTEND_URL=http://localhost:3000
```

Crie o `.gitignore`:

```gitignore
venv/
.env
__pycache__/
*.pyc
.pytest_cache/
htmlcov/
```

---

## Passo 5 — Configuração e banco de dados

**`app/core/config.py`**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    CORE_URL: str
    SECRET_KEY: str
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"

settings = Settings()
```

> Instale também: `pip install pydantic-settings` e adicione ao requirements.txt

**`app/core/database.py`**

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## Passo 6 — Models (tabelas do banco)

**`app/models/produto.py`**

```python
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Produto(Base):
    __tablename__ = "produtos"

    id            = Column(Integer, primary_key=True, index=True)
    codigo        = Column(String(50), unique=True, nullable=False)  # SKU
    descricao     = Column(String(200), nullable=False)
    unidade       = Column(String(20), nullable=False, default="un")
    quantidade    = Column(Integer, default=0)
    estoque_minimo = Column(Integer, nullable=False)
    custo         = Column(Numeric(15, 2), nullable=False, default=0)
    ativo         = Column(Boolean, default=True)
    criado_em     = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
```

**`app/models/movimentacao.py`**

```python
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class TipoMovimentacao(str, enum.Enum):
    entrada  = "entrada"
    saida    = "saida"
    ajuste   = "ajuste"

class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    id              = Column(Integer, primary_key=True, index=True)
    produto_id      = Column(Integer, nullable=False)
    usuario_id      = Column(Integer, nullable=False)   # vem do JWT
    tipo            = Column(Enum(TipoMovimentacao), nullable=False)
    quantidade      = Column(Integer, nullable=False)
    motivo          = Column(String(200))
    fornecedor_id   = Column(Integer)
    nota_fiscal     = Column(String(50))
    centro_custo    = Column(String(50))
    ordem_compra_id = Column(Integer)
    justificativa   = Column(String(500))               # para ajustes
    criado_em       = Column(DateTime(timezone=True), server_default=func.now())
```

---

## Passo 7 — Schemas (formato da API)

**`app/schemas/produto.py`**

```python
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class ProdutoCreate(BaseModel):
    codigo: str
    descricao: str
    unidade: str = "un"
    estoque_minimo: int
    quantidade: int = 0
    custo: Decimal = Decimal("0.00")

class ProdutoUpdate(BaseModel):
    descricao: Optional[str] = None
    unidade: Optional[str] = None
    estoque_minimo: Optional[int] = None
    custo: Optional[Decimal] = None

class ProdutoResponse(BaseModel):
    id: int
    codigo: str
    descricao: str
    unidade: str
    quantidade: int
    estoque_minimo: int
    custo: Decimal
    ativo: bool
    status: str  # "Normal" ou "Reposicao" — calculado

    class Config:
        from_attributes = True
```

**`app/schemas/movimentacao.py`**

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EntradaCreate(BaseModel):
    produto_id: int
    quantidade: int
    fornecedor_id: Optional[int] = None
    nota_fiscal: Optional[str] = None
    ordem_compra_id: Optional[int] = None

class SaidaCreate(BaseModel):
    produto_id: int
    quantidade: int
    motivo: str
    centro_custo: Optional[str] = None

class AjusteCreate(BaseModel):
    quantidade_nova: int
    justificativa: str

class MovimentacaoResponse(BaseModel):
    id: int
    produto_id: int
    tipo: str
    quantidade: int
    criado_em: datetime

    class Config:
        from_attributes = True
```

---

## Passo 8 — Service (regras de negócio)

**`app/services/estoque_service.py`**

```python
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.produto import Produto
from app.models.movimentacao import Movimentacao, TipoMovimentacao
from app.schemas.movimentacao import EntradaCreate, SaidaCreate

def registrar_entrada(db: Session, dados: EntradaCreate, usuario_id: int):
    produto = db.query(Produto).filter(Produto.id == dados.produto_id, Produto.ativo == True).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    produto.quantidade += dados.quantidade

    mov = Movimentacao(
        produto_id=dados.produto_id,
        usuario_id=usuario_id,
        tipo=TipoMovimentacao.entrada,
        quantidade=dados.quantidade,
        fornecedor_id=dados.fornecedor_id,
        nota_fiscal=dados.nota_fiscal,
        ordem_compra_id=dados.ordem_compra_id,
    )
    db.add(mov)
    db.commit()
    db.refresh(produto)
    return mov

def registrar_saida(db: Session, dados: SaidaCreate, usuario_id: int):
    produto = db.query(Produto).filter(Produto.id == dados.produto_id, Produto.ativo == True).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # REGRA CENTRAL: estoque nunca negativo
    if produto.quantidade - dados.quantidade < 0:
        raise HTTPException(
            status_code=422,
            detail=f"Saldo insuficiente. Disponível: {produto.quantidade}"
        )

    produto.quantidade -= dados.quantidade

    mov = Movimentacao(
        produto_id=dados.produto_id,
        usuario_id=usuario_id,
        tipo=TipoMovimentacao.saida,
        quantidade=dados.quantidade,
        motivo=dados.motivo,
        centro_custo=dados.centro_custo,
    )
    db.add(mov)
    db.commit()
    return mov
```

---

## Passo 9 — Routers (endpoints)

**`app/routers/produtos.py`**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.produto import Produto
from app.schemas.produto import ProdutoCreate, ProdutoUpdate, ProdutoResponse
from typing import List

router = APIRouter(prefix="/estoque/produtos", tags=["Produtos"])

@router.get("/", response_model=List[ProdutoResponse])
def listar_produtos(page: int = 1, size: int = 10, db: Session = Depends(get_db)):
    offset = (page - 1) * size
    produtos = db.query(Produto).filter(Produto.ativo == True).offset(offset).limit(size).all()
    for p in produtos:
        p.status = "Reposicao" if p.quantidade < p.estoque_minimo else "Normal"
    return produtos

@router.post("/", response_model=ProdutoResponse, status_code=201)
def cadastrar_produto(dados: ProdutoCreate, db: Session = Depends(get_db)):
    existente = db.query(Produto).filter(Produto.codigo == dados.codigo).first()
    if existente:
        raise HTTPException(status_code=400, detail="SKU já cadastrado")
    produto = Produto(**dados.model_dump())
    db.add(produto)
    db.commit()
    db.refresh(produto)
    produto.status = "Reposicao" if produto.quantidade < produto.estoque_minimo else "Normal"
    return produto

@router.get("/{id}", response_model=ProdutoResponse)
def detalhar_produto(id: int, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == id, Produto.ativo == True).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    produto.status = "Reposicao" if produto.quantidade < produto.estoque_minimo else "Normal"
    return produto

@router.put("/{id}", response_model=ProdutoResponse)
def atualizar_produto(id: int, dados: ProdutoUpdate, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == id, Produto.ativo == True).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(produto, campo, valor)
    db.commit()
    db.refresh(produto)
    produto.status = "Reposicao" if produto.quantidade < produto.estoque_minimo else "Normal"
    return produto
```

**`app/routers/alertas.py`**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.produto import Produto

router = APIRouter(prefix="/estoque", tags=["Alertas"])

@router.get("/alertas")
def listar_alertas(db: Session = Depends(get_db)):
    produtos = db.query(Produto).filter(
        Produto.ativo == True,
        Produto.quantidade < Produto.estoque_minimo
    ).all()
    return {
        "total": len(produtos),
        "produtos": [
            {
                "id": p.id,
                "codigo": p.codigo,
                "descricao": p.descricao,
                "unidade": p.unidade,
                "quantidade": p.quantidade,
                "estoque_minimo": p.estoque_minimo,
            }
            for p in produtos
        ]
    }
```

**`app/routers/movimentacoes.py`**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.movimentacao import Movimentacao
from app.schemas.movimentacao import EntradaCreate, SaidaCreate, MovimentacaoResponse
from app.services.estoque_service import registrar_entrada, registrar_saida
from typing import List

router = APIRouter(prefix="/estoque/movimentacoes", tags=["Movimentações"])

# usuario_id fixo em 1 por enquanto — depois substituir pelo JWT
@router.post("/entrada", status_code=201)
def entrada(dados: EntradaCreate, db: Session = Depends(get_db)):
    return registrar_entrada(db, dados, usuario_id=1)

@router.post("/saida", status_code=201)
def saida(dados: SaidaCreate, db: Session = Depends(get_db)):
    return registrar_saida(db, dados, usuario_id=1)

@router.get("/{prod_id}", response_model=List[MovimentacaoResponse])
def historico(prod_id: int, db: Session = Depends(get_db)):
    return db.query(Movimentacao).filter(Movimentacao.produto_id == prod_id).all()
```

---

## Passo 10 — Main (junta tudo)

**`app/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine
from app.routers import produtos, movimentacoes, alertas

# Cria as tabelas no Supabase automaticamente
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Módulo Estoque — ERP Universitário",
    description="API REST para controle de estoque e almoxarifado",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(produtos.router)
app.include_router(movimentacoes.router)
app.include_router(alertas.router)

@app.get("/health")
def health():
    return {"status": "ok", "modulo": "estoque"}
```

---

## Passo 11 — Rodar localmente

```bash
uvicorn app.main:app --reload --port 8003
```

Acesse:

- **Swagger (documentação interativa):** http://localhost:8003/docs
- **Health check:** http://localhost:8003/health

Ao rodar pela primeira vez, o SQLAlchemy vai criar as tabelas automaticamente no seu banco Supabase. Você pode confirmar em **Supabase → Table Editor**.

---

## Passo 12 — Criar as migrações com Alembic

O Alembic serve para versionar mudanças no banco — importante para o projeto avaliado.

```bash
alembic init alembic
```

Edite o arquivo `alembic/env.py`, encontre a linha `target_metadata = None` e substitua por:

```python
from app.core.database import Base
from app.models import produto, movimentacao  # importa todos os models
target_metadata = Base.metadata
```

Edite também o `alembic.ini`, encontre `sqlalchemy.url` e substitua por:

```ini
sqlalchemy.url = %(DATABASE_URL)s
```

E no `alembic/env.py` adicione no início:

```python
import os
from dotenv import load_dotenv
load_dotenv()
```

Gerar e rodar a primeira migration:

```bash
alembic revision --autogenerate -m "criar tabelas iniciais"
alembic upgrade head
```

---

## Passo 13 — Deploy no Railway

1. Faça push do projeto para um repositório no GitHub (sem o `.env`)
2. Acesse [railway.app](https://railway.app) e crie uma conta
3. Clique em **New Project → Deploy from GitHub repo**
4. Selecione seu repositório
5. Em **Variables**, adicione todas as variáveis do seu `.env`:
   - `DATABASE_URL`
   - `CORE_URL`
   - `SECRET_KEY`
   - `FRONTEND_URL`
6. Em **Settings**, defina o comando de start:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
7. O Railway vai gerar uma URL pública tipo `https://modulo-estoque.up.railway.app`

Passe essa URL para o grupo do Frontend e do Core.

---

## Próximos passos (após o básico rodar)

| Prioridade | O que fazer                                                      |
| ---------- | ---------------------------------------------------------------- |
| Alta       | Adicionar validação de JWT nos endpoints (integrar com o Core)   |
| Alta       | Criar script de seed com dados de exemplo (`seed.py`)            |
| Alta       | Escrever testes com pytest (mínimo 70% de cobertura)             |
| Média      | Adicionar router de inventário (`/estoque/inventario/{prod_id}`) |
| Média      | Adicionar paginação e filtros nas listagens                      |
| Baixa      | Adicionar Docker Compose para bônus (+0,5 na nota)               |

---

## Resumo dos comandos do dia a dia

```bash
# ativar o ambiente virtual
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# rodar o servidor local
uvicorn app.main:app --reload --port 8003

# criar nova migration após mudar um model
alembic revision --autogenerate -m "descricao da mudanca"
alembic upgrade head

# rodar os testes
pytest --cov=app tests/

# ver a cobertura no navegador
pytest --cov=app --cov-report=html tests/
# abrir htmlcov/index.html
```

---

> **Dica final:** Comece pelo Passo 11 — só rodar o servidor e ver o Swagger funcionando já é motivador. Não tente implementar tudo de uma vez. Faça um endpoint funcionar completamente antes de partir para o próximo.
