from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.movimentacao import MovimentacaoEstoque, TipoMovimentacao
from app.models.produto import Produto
from app.schemas.movimentacao import EntradaCreate, InventarioCreate, SaidaCreate


def registrar_entrada(db: Session, dados: EntradaCreate) -> MovimentacaoEstoque:
    produto = db.query(Produto).filter(Produto.id == dados.produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    produto.saldo_atual += dados.quantidade

    mov = MovimentacaoEstoque(
        produto_id=dados.produto_id,
        tipo=TipoMovimentacao.entrada.value,
        quantidade=dados.quantidade,
    )
    db.add(mov)
    db.commit()
    db.refresh(mov)
    return mov


def registrar_saida(db: Session, dados: SaidaCreate) -> MovimentacaoEstoque:
    produto = db.query(Produto).filter(Produto.id == dados.produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    if produto.saldo_atual - dados.quantidade < 0:
        raise HTTPException(
            status_code=422, detail=f"Saldo insuficiente. Disponível: {produto.saldo_atual}"
        )

    produto.saldo_atual -= dados.quantidade

    mov = MovimentacaoEstoque(
        produto_id=dados.produto_id,
        tipo=TipoMovimentacao.saida.value,
        quantidade=dados.quantidade,
    )
    db.add(mov)
    db.commit()
    db.refresh(mov)
    return mov


def registrar_inventario(
    db: Session, produto_id: int, dados: InventarioCreate
) -> MovimentacaoEstoque:
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    produto.saldo_atual = dados.saldo_ajustado

    mov = MovimentacaoEstoque(
        produto_id=produto_id,
        tipo=TipoMovimentacao.inventario.value,
        quantidade=dados.saldo_ajustado,
        justificativa=dados.justificativa,
        saldo_ajustado=dados.saldo_ajustado,
    )
    db.add(mov)
    db.commit()
    db.refresh(mov)
    return mov
