from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProdutoCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    nome: str
    sku: str
    unidade: str = "un"
    saldo_atual: int = Field(0, ge=0, alias="saldoAtual")
    estoque_minimo: int = Field(0, ge=0, alias="estoqueMinimo")


class ProdutoUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    nome: Optional[str] = None
    unidade: Optional[str] = None
    saldo_atual: Optional[int] = Field(None, ge=0, alias="saldoAtual")
    estoque_minimo: Optional[int] = Field(None, ge=0, alias="estoqueMinimo")


class ProdutoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    nome: str
    sku: str
    unidade: str
    saldo_atual: int = Field(..., ge=0, alias="saldoAtual")
    estoque_minimo: int = Field(..., ge=0, alias="estoqueMinimo")
    status: str
