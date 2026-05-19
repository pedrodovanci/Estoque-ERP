from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.movimentacao import MovimentacaoEstoque
from app.models.produto import Produto
from app.schemas.produto import ProdutoCreate, ProdutoResponse, ProdutoUpdate

def _require_service_token(x_service_token: str | None = Header(None, alias="X-Service-Token")):
    if not settings.SERVICE_TOKEN:
        return
    if x_service_token != settings.SERVICE_TOKEN:
        raise HTTPException(status_code=401, detail="Não autorizado")


router = APIRouter(
    prefix="/estoque/produtos",
    tags=["Produtos"],
    dependencies=[Depends(_require_service_token)],
)


def _status(produto: Produto) -> str:
    return "Reposicao" if produto.saldo_atual < produto.estoque_minimo else "Normal"


@router.get("/", response_model=List[ProdutoResponse])
def listar_produtos(
    page: int = 1,
    size: int = 10,
    sku: str | None = None,
    db: Session = Depends(get_db),
):
    offset = (page - 1) * size
    query = db.query(Produto)
    if sku:
        query = query.filter(Produto.sku == sku)
    produtos = query.offset(offset).limit(size).all()
    for p in produtos:
        p.status = _status(p)
    return produtos


@router.post("/", response_model=ProdutoResponse, status_code=201)
def cadastrar_produto(dados: ProdutoCreate, db: Session = Depends(get_db)):
    existente = db.query(Produto).filter(Produto.sku == dados.sku).first()
    if existente:
        raise HTTPException(status_code=400, detail="SKU já cadastrado")

    produto = Produto(**dados.model_dump())
    db.add(produto)
    db.commit()
    db.refresh(produto)
    produto.status = _status(produto)
    return produto


@router.get("/{id}", response_model=ProdutoResponse)
def detalhar_produto(id: int, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    produto.status = _status(produto)
    return produto


@router.put("/{id}", response_model=ProdutoResponse)
def atualizar_produto(id: int, dados: ProdutoUpdate, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(produto, campo, valor)
    db.commit()
    db.refresh(produto)
    produto.status = _status(produto)
    return produto


@router.delete("/{id}", status_code=204)
def excluir_produto(id: int, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    tem_movimentacao = (
        db.query(MovimentacaoEstoque.id)
        .filter(MovimentacaoEstoque.produto_id == id)
        .first()
        is not None
    )
    if tem_movimentacao:
        raise HTTPException(
            status_code=409,
            detail="Não é possível excluir produto com movimentações registradas",
        )

    db.delete(produto)
    db.commit()
