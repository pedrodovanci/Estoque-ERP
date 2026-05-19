import enum

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.core.database import Base


class TipoMovimentacao(str, enum.Enum):
    entrada = "entrada"
    saida = "saida"
    inventario = "inventario"


class MovimentacaoEstoque(Base):
    __tablename__ = "movimentacoes_estoque"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, nullable=False)
    tipo = Column(String(20), nullable=False)
    quantidade = Column(Integer, nullable=False)
    justificativa = Column(String(500))
    saldo_ajustado = Column(Integer)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
