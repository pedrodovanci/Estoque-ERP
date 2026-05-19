from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EntradaCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    produto_id: int = Field(..., alias="produtoId")
    quantidade: int = Field(..., gt=0)


class SaidaCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    produto_id: int = Field(..., alias="produtoId")
    quantidade: int = Field(..., gt=0)
    motivo: Optional[str] = None


class InventarioCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    saldo_ajustado: int = Field(..., ge=0, alias="saldoAjustado")
    justificativa: str


class MovimentacaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    produto_id: int = Field(..., alias="produtoId")
    tipo: str
    quantidade: int
    saldo_ajustado: Optional[int] = Field(None, alias="saldoAjustado")
    criado_em: datetime
