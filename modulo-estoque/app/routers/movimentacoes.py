from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.movimentacao import MovimentacaoEstoque
from app.schemas.movimentacao import EntradaCreate, MovimentacaoResponse, SaidaCreate
from app.services.estoque_service import registrar_entrada, registrar_saida

def _require_service_token(x_service_token: str | None = Header(None, alias="X-Service-Token")):
    if not settings.SERVICE_TOKEN:
        return
    if x_service_token != settings.SERVICE_TOKEN:
        raise HTTPException(status_code=401, detail="Não autorizado")


router = APIRouter(
    prefix="/estoque/movimentacoes",
    tags=["Movimentações"],
    dependencies=[Depends(_require_service_token)],
)


@router.post("/entrada", response_model=MovimentacaoResponse, status_code=201)
def entrada(
    dados: EntradaCreate,
    db: Session = Depends(get_db),
):
    return registrar_entrada(db, dados)


@router.post("/saida", response_model=MovimentacaoResponse, status_code=201)
def saida(
    dados: SaidaCreate,
    db: Session = Depends(get_db),
):
    return registrar_saida(db, dados)


@router.get("/{prod_id}", response_model=List[MovimentacaoResponse])
def historico(prod_id: int, db: Session = Depends(get_db)):
    return (
        db.query(MovimentacaoEstoque)
        .filter(MovimentacaoEstoque.produto_id == prod_id)
        .order_by(MovimentacaoEstoque.criado_em.desc())
        .all()
    )
