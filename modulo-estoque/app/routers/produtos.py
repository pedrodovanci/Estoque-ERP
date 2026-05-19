from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.produto import Produto
from app.schemas.produto import ProdutoCreate, ProdutoResponse, ProdutoUpdate

router = APIRouter(prefix="/estoque/produtos", tags=["Produtos"])


def _status(produto: Produto) -> str:
    return "Reposicao" if produto.saldo_atual < produto.estoque_minimo else "Normal"


@router.get("/", response_model=List[ProdutoResponse])
def listar_produtos(page: int = 1, size: int = 10, db: Session = Depends(get_db)):
    offset = (page - 1) * size
    produtos = db.query(Produto).offset(offset).limit(size).all()
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
