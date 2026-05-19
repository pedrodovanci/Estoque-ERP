from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.produto import Produto
from app.schemas.movimentacao import InventarioCreate, MovimentacaoResponse
from app.services.estoque_service import registrar_inventario

router = APIRouter(prefix="/estoque", tags=["Alertas"])


@router.get("/alertas")
def listar_alertas(db: Session = Depends(get_db)):
    produtos = (
        db.query(Produto)
        .filter(Produto.saldo_atual < Produto.estoque_minimo)
        .all()
    )
    return {
        "total": len(produtos),
        "produtos": [
            {
                "id": p.id,
                "nome": p.nome,
                "sku": p.sku,
                "unidade": p.unidade,
                "saldoAtual": p.saldo_atual,
                "estoqueMinimo": p.estoque_minimo,
            }
            for p in produtos
        ],
    }


@router.post("/inventario/{prod_id}", response_model=MovimentacaoResponse, status_code=201)
def inventario(prod_id: int, dados: InventarioCreate, db: Session = Depends(get_db)):
    return registrar_inventario(db, produto_id=prod_id, dados=dados)
